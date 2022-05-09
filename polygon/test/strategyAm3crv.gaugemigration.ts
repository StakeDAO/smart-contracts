import { ethers, network } from "hardhat";
import { expect } from "chai";
import { BigNumber } from "@ethersproject/bignumber";
import { Contract } from "@ethersproject/contracts";
import { parseEther } from "@ethersproject/units";
import { JsonRpcSigner } from "@ethersproject/providers";

import Controller from "../abis/Controller.json";
import YVault from "../abis/YVault.json";
import ERC20 from "../abis/ERC20.json";
import ICurveGauge from "../abis/ICurveGauge.json";

const VAULT = "0x7d60F21072b585351dFd5E8b17109458D97ec120";
const CONTROLLER = "0x91aE00aaC6eE0D7853C8F92710B641F68Cd945Df";
const GOVERNANCE = "0xb36a0671B3D49587236d7833B01E79798175875f";
const OLD_STRATEGY = "0xe7E66372f19C3E5Fc4D6c3c88c54178Bcd525040";
const OLD_GAUGE = "0x19793B454D3AfC7b454F206Ffe95aDE26cA6912c";
const CRV = "0x172370d5Cd63279eFa6d502DAB29171933a610AF";
const WANT = "0xE7a24EF0C5e95Ffb0f6684b813A78F2a3AD7D171"; // am3CRV
const NEWGAUGE = "0x20759F567BB3EcDB55c817c9a1d13076aB215EdC";
describe("StrategyAm3Crv Gauge Migration", function () {
	let vault: Contract;
	let want: Contract;
	let crv: Contract;
	let controller: Contract;
	let currentStrategy: Contract;
	let crvGauge: Contract;
	let governanceSigner: JsonRpcSigner;

	let initialBalance: BigNumber;

	before(async function () {
		const [owner] = await ethers.getSigners();

		await network.provider.request({
			method: "hardhat_impersonateAccount",
			params: [CONTROLLER],
		});

		await network.provider.request({
			method: "hardhat_impersonateAccount",
			params: [GOVERNANCE],
		});

		vault = await ethers.getContractAt(YVault, VAULT);
		controller = await ethers.getContractAt(Controller, CONTROLLER);
		want = await ethers.getContractAt(ERC20, WANT);
		crv = await ethers.getContractAt(ERC20, CRV);
		crvGauge = await ethers.getContractAt(ICurveGauge, OLD_GAUGE);
		currentStrategy = await ethers.getContractAt(
			"StrategyAm3Crv",
			OLD_STRATEGY
		);

		governanceSigner = await ethers.provider.getSigner(GOVERNANCE);

		initialBalance = await vault.balance();
	});

	it("Migrate Gauge", async function () {
		await controller.connect(governanceSigner).withdrawAll(WANT);
		let availableBalance = await vault.available();

		await currentStrategy.connect(governanceSigner).setGauge(NEWGAUGE);
		await vault.earn();

		expect(availableBalance).to.be.eq(
			await currentStrategy.callStatic.balanceOfPool()
		);

		// Testing old gauge award remains
		expect(
			await crvGauge.claimable_reward(
				currentStrategy.address,
				"0x172370d5Cd63279eFa6d502DAB29171933a610AF"
			)
		).to.eq(0);
		expect(
			await crvGauge.claimable_reward(
				currentStrategy.address,
				"0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
			)
		).to.eq(0);
	});
});
