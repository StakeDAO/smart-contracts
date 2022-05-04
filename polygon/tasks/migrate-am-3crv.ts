import { ethers, network, waffle } from "hardhat";
import { Contract } from "@ethersproject/contracts";
import Controller from "../abis/Controller.json";
import YVault from "../abis/YVault.json";

(async () => {
	let [ownerAcc] = await ethers.getSigners();
	let controller: Contract;
	let vault: Contract;
	let currentStrategy: Contract;

	const WANT = "0xE7a24EF0C5e95Ffb0f6684b813A78F2a3AD7D171"; // am3CRV
	const CONTROLLER = "0x91aE00aaC6eE0D7853C8F92710B641F68Cd945Df";
	const VAULT = "0x7d60F21072b585351dFd5E8b17109458D97ec120";
	const NEWGAUGE = "0x20759F567BB3EcDB55c817c9a1d13076aB215EdC";
	const CURRENT_STRATEGY = "0xe7E66372f19C3E5Fc4D6c3c88c54178Bcd525040";

	controller = await ethers.getContractAt(Controller, CONTROLLER);
	vault = await ethers.getContractAt(YVault, VAULT);
	currentStrategy = await ethers.getContractAt(
		"StrategyAm3Crv",
		CURRENT_STRATEGY
	);

	// Withdraw
	await controller.withdrawAll(WANT);
	console.log("Withdrawn");
	// Set new gauge
	await currentStrategy.setGauge(NEWGAUGE);
	console.log("new gauge set");
	// Call Earn
	await vault.earn();
	console.log("earned call");
})();
