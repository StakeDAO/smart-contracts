import { ethers, network, waffle } from "hardhat";
import StrategyBtcCurveArtifact from "../artifacts/contracts/StrategyBtcCurve.sol/StrategyBtcCurve.json";
import { StrategyBtcCurve } from "../typechain";
const { deployContract } = waffle;
import { Contract } from "@ethersproject/contracts";
import Controller from "../abis/Controller.json";
import YVault from '../abis/YVault.json';

(async () => {
	let [ownerAcc] = await ethers.getSigners();
	let controller: Contract;
    let vault: Contract;
	let StrategyBtcCurve: StrategyBtcCurve;
	const WANT = "0xf8a57c1d3b9629b77b6726a042ca48990a84fb49"; // am3CRV
	const CONTROLLER = "0x91aE00aaC6eE0D7853C8F92710B641F68Cd945Df";
    const VAULT = '0x953Cf8f1f097c222015FFa32C7B9e3E96993b8c1';
	let args = [CONTROLLER];

	controller = await ethers.getContractAt(Controller, CONTROLLER);
    vault = await ethers.getContractAt(YVault, VAULT);

    //Deploy strategy
	StrategyBtcCurve = (await deployContract(
		ownerAcc,
		StrategyBtcCurveArtifact,
		args
	)) as StrategyBtcCurve;
	console.log(
		"Deployed StrategyBtcCurve contract deployed at " + StrategyBtcCurve.address
	);
	console.log(
		`npx hardhat verify --network ${network.name} ${
			StrategyBtcCurve.address
		} ${args.join(" ")}`
	);

    // Approve & set strategy
	await controller.approveStrategy(WANT, StrategyBtcCurve.address);
	console.log('Approved strategy')
	await controller.setStrategy(WANT, StrategyBtcCurve.address);
	console.log('Set strategy')

    // Call Earn
    await vault.earn()
    await vault.earn()
    await vault.earn()
	console.log('Earn called')
})();
