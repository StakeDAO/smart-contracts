import { ethers, network } from "hardhat";
import { expect } from "chai";
import { BigNumber } from "@ethersproject/bignumber";
import { Contract } from "@ethersproject/contracts";
import { JsonRpcSigner } from "@ethersproject/providers";

import ERC20ABI from "./fixtures/ERC20.json";

const WANT = "0x1337BedC9D22ecbe766dF105c9623922A27963EC";
const WANT_HOLDER = "0x5ede2CBA38aE20EAc6dF5595651e4f8E5084940B";

describe("Aave strat", function () {
	let controller: Contract;
	let vault: Contract;
	let strategy: Contract;
	let want: Contract;
	let holderSigner: JsonRpcSigner;
	let initialHolderBalance: BigNumber;

	before(async function () {
		const [owner] = await ethers.getSigners();

		await network.provider.request({
			method: "hardhat_impersonateAccount",
			params: [WANT_HOLDER],
		});

		const Controller = await ethers.getContractFactory("Controller");
		const Vault = await ethers.getContractFactory("Vault");
		const Strategy = await ethers.getContractFactory("StrategyCurveAave");

		controller = await Controller.deploy(owner.address);
		vault = await Vault.deploy(WANT, controller.address, owner.address, "StakeDAO", "sd");
		strategy = await Strategy.deploy(controller.address);

		want = await ethers.getContractAt(ERC20ABI, WANT);
		holderSigner = await ethers.provider.getSigner(WANT_HOLDER);

		await (await controller.approveStrategy(WANT, strategy.address)).wait();
		await (await controller.setStrategy(WANT, strategy.address)).wait();
		await (await controller.setVault(WANT, vault.address)).wait();

		// approve
		initialHolderBalance = await want.balanceOf(WANT_HOLDER);
		await (await want.connect(holderSigner).approve(vault.address, initialHolderBalance)).wait();
	});

	it("Should deposit in vault", async function () {
		const holderBalance = await want.balanceOf(WANT_HOLDER);
		await (await vault.connect(holderSigner).deposit(holderBalance)).wait();
		const vaultBalance = await want.balanceOf(vault.address);
		expect(vaultBalance).to.be.equal(holderBalance);
	});

	it("Should deposit in strategy", async function () {
		const vaultBalance = await want.balanceOf(vault.address);
		await (await vault.earn()).wait();
		const strategyBalance = await strategy.balanceOfPool();
		expect(vaultBalance).to.be.equal(strategyBalance);
	});

	it("Should harvest", async function () {
		await network.provider.send("evm_increaseTime", [3600]);
		await network.provider.send("evm_mine");

		const strategyBalanceBefore = await strategy.balanceOf();
		await (await strategy.harvest()).wait();
		const strategyBalanceAfter = await strategy.balanceOf();
		expect(strategyBalanceAfter).to.be.gt(strategyBalanceBefore);
	});

	it("Should withdraw all", async function () {
		const holderBalanceBefore = await want.balanceOf(WANT_HOLDER);
		const holderSDBalanceBefore = await vault.balanceOf(WANT_HOLDER);
		const withdrawAmount = holderSDBalanceBefore;

		const pricePerShare = await vault.getPricePerFullShare();

		await (await vault.connect(holderSigner).withdraw(withdrawAmount)).wait();

		const holderBalanceAfter = await want.balanceOf(WANT_HOLDER);
		const holderSDBalanceAfter = await vault.balanceOf(WANT_HOLDER);

		const withdrawInWant = withdrawAmount.mul(pricePerShare).div(BigNumber.from(10).pow(18));
		const fees = withdrawInWant.mul(50).div(10000);

		const expected = holderBalanceBefore.add(withdrawInWant).sub(fees);

		console.log({
			expected: expected.toString(),
			holderBalanceAfter: holderBalanceAfter.toString(),
		});

		expect(holderBalanceAfter).to.be.equal(expected);

		// correct SD amount has be withdrawn
		expect(holderSDBalanceBefore.sub(withdrawAmount)).to.be.equal(holderSDBalanceAfter);

		// you won some (even with 0.5% withdrawal fees)
		expect(holderBalanceAfter).to.be.gt(initialHolderBalance.mul(995).div(1000));
	});
});
