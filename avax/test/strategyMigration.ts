import { ethers, network } from "hardhat";
import { expect } from "chai";
import { BigNumber } from "@ethersproject/bignumber";
import { Contract } from "@ethersproject/contracts";
import { JsonRpcSigner } from "@ethersproject/providers";

import ERC20ABI from "./fixtures/ERC20.json";

const CONTROLLER = "0x01f0ea8d52247428A7CEF21327f78d7E00d37502";
const CONTROLLER_ADMIN = "0xb36a0671b3d49587236d7833b01e79798175875f";
const AAVE_STRATEGY = "0x22D0b68a88BCFf9A0D9F08fFf03dd969Eed094Ca";
const VAULT = "0x0665eF3556520B21368754Fb644eD3ebF1993AD4";
const CRV = "0x47536F17F4fF30e64A96a7555826b8f9e66ec468";

describe("Aave strategy migration", function () {
	let controller: Contract;
	let vault: Contract;
	let strategy: Contract;
    let strategyNew: Contract;
	let crv: Contract;
    let want: Contract;
	let controllerAdmmin: JsonRpcSigner;

	before(async function () {
		const [owner] = await ethers.getSigners();
		
		await network.provider.request({
			method: "hardhat_impersonateAccount",
			params: [CONTROLLER_ADMIN]
		});

        const StrategyNew = await ethers.getContractFactory("StrategyCurveAaveNew");
        controllerAdmmin = await ethers.provider.getSigner(CONTROLLER_ADMIN);
		controller = await ethers.getContractAt("Controller", CONTROLLER);
        vault = await ethers.getContractAt("Vault", VAULT);
		strategyNew = await StrategyNew.deploy(CONTROLLER);
        strategy = await ethers.getContractAt("StrategyCurveAave", AAVE_STRATEGY);
        crv = await ethers.getContractAt(ERC20ABI, CRV);
        want = await ethers.getContractAt(ERC20ABI, vault.token());
	});

	it("Should withdraw all CRV in stuck before the migration", async function () {
        const strategyCrvBalance = await crv.balanceOf(strategy.address);
        await controller.connect(controllerAdmmin).inCaseStrategyTokenGetStuck(strategy.address, crv.address);
        const controllerCrvBalance = await crv.balanceOf(controller.address);
        expect(controllerCrvBalance).to.be.eq(strategyCrvBalance);
        const strategyCrvBalanceAfter = await crv.balanceOf(strategy.address);
        expect(strategyCrvBalanceAfter).to.be.eq(0);
	});

	it("Should set the new strategy via controller and call earn in vault", async function () {
        this.enableTimeouts(false);
        const strategyWantBefore = await strategy.balanceOfPool();
        await strategy.connect(controllerAdmmin).harvest();
        const strategyWantAfter = await strategy.balanceOfPool();
        expect(strategyWantAfter).to.be.gt(strategyWantBefore);
        await controller.connect(controllerAdmmin).approveStrategy(want.address, strategyNew.address);
        const vaultWantBefore = await want.balanceOf(vault.address);
        await controller.connect(controllerAdmmin).setStrategy(want.address, strategyNew.address);
        const vaultWantAfter = await want.balanceOf(vault.address);
        const wantReceived = vaultWantAfter.sub(vaultWantBefore);
        expect(strategyWantAfter).to.be.eq(wantReceived);
        await vault.earn();
        const newStrategyWant = await strategyNew.balanceOfPool();
        expect(newStrategyWant).to.be.eq(vaultWantAfter);
	});

	it("Should call harvest in strategy", async function () {
        const strategyBefore = await strategyNew.balanceOfPool();
        await network.provider.send("evm_increaseTime", [86400 * 2]); // 2 days
        await network.provider.send("evm_mine", []);
        await strategyNew.harvest();
        const strategyAfter = await strategyNew.balanceOfPool();
        expect(strategyAfter).to.be.gt(strategyBefore);
	});
});
