import { ethers, network } from "hardhat";
import { expect } from "chai";
import { BigNumber } from "@ethersproject/bignumber";
import { Contract } from "@ethersproject/contracts";
import { JsonRpcSigner } from "@ethersproject/providers";

import ERC20ABI from "./fixtures/ERC20.json";
import { parseEther } from "@ethersproject/units";

const WANT = "0x0665eF3556520B21368754Fb644eD3ebF1993AD4"; // sdav3CRV
const WANT_HOLDER = "0xe582c162c9C06F48b8286cbFD7e0257FB1d47ec2"; // sdav3CRV holder
const WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7";
const WAVAX_HOLDER = "0x331d3D8f0c4618B22e1BBe0c262e09d46821a441"; 
const DEPLOYER = "0xb36a0671B3D49587236d7833B01E79798175875f"; // sd deployer
const SDT = "0x8323FCF06D58F49533Da60906D731c6a56626Fb2";
const SDT_HOLDER = "0x0411e650dff0c6680c9e147f2413e0480718aa27";

describe("Gauge multi rewards", function () {
	let vault: Contract;
    let gauge: Contract;
	let sdav3CRV: Contract;
    let wavax: Contract;
    let sdt: Contract;
	let holderSigner: JsonRpcSigner;
	let deployerSigner: JsonRpcSigner;
    let wavaxHolder: JsonRpcSigner;
    let sdtHolder: JsonRpcSigner;

	before(async function () {
		const [owner] = await ethers.getSigners();

		await network.provider.request({
			method: "hardhat_impersonateAccount",
			params: [WANT_HOLDER],
		});

        await network.provider.request({
			method: "hardhat_impersonateAccount",
			params: [DEPLOYER],
		});

        await network.provider.request({
			method: "hardhat_impersonateAccount",
			params: [WAVAX_HOLDER],
		});

        await network.provider.request({
			method: "hardhat_impersonateAccount",
			params: [SDT_HOLDER],
		});

        holderSigner = await ethers.provider.getSigner(WANT_HOLDER);
        deployerSigner = await ethers.provider.getSigner(DEPLOYER);
        wavaxHolder = await ethers.provider.getSigner(WAVAX_HOLDER);
        sdtHolder = await ethers.provider.getSigner(SDT_HOLDER);

		const Gauge = await ethers.getContractFactory("MultiRewards");

		sdav3CRV = await ethers.getContractAt(ERC20ABI, WANT);
        wavax = await ethers.getContractAt(ERC20ABI, WAVAX);
        sdt = await ethers.getContractAt(ERC20ABI, SDT);

        await wavax.connect(wavaxHolder).transfer(deployerSigner._address, parseEther("1000"))
        await sdt.connect(sdtHolder).transfer(deployerSigner._address, parseEther("10"))

        gauge = await Gauge.connect(deployerSigner).deploy(sdav3CRV.address);
        await gauge.addReward(WAVAX, deployerSigner._address, 86400 * 3); // 3 days of reward

	});

    it("Should notify WAVAX reward", async function () {
        const amount = parseEther("1000")
        await wavax.connect(deployerSigner).approve(gauge.address, amount)
        await gauge.connect(deployerSigner).notifyRewardAmount(WAVAX, amount)
        const gaugeBalance = await wavax.balanceOf(gauge.address)
        expect(gaugeBalance).to.be.eq(amount)
	});

    it("Should deposit into the gauge", async function () {
        const amount = parseEther("10")
        await sdav3CRV.connect(holderSigner).approve(gauge.address, amount)
		await gauge.connect(holderSigner).stake(amount);
		const gaugeBalance = await sdav3CRV.balanceOf(gauge.address);
		expect(gaugeBalance).to.be.eq(amount);
	});

    it("Should get reward in AVAX", async function () {
        await network.provider.send("evm_increaseTime", [86400 * 2]); // 1 day
        await network.provider.send("evm_mine", []);
        await gauge.connect(holderSigner).getReward()
        const balance = await wavax.balanceOf(holderSigner._address)
        expect(balance).to.be.gt(0)
	});

    it("Add and notify reward in SDT", async function () {
        const sdtAmount = parseEther("10")
        await gauge.addReward(SDT, deployerSigner._address, 86400 * 3)
        await sdt.connect(deployerSigner).approve(gauge.address, sdtAmount)
        await gauge.notifyRewardAmount(SDT, sdtAmount)
	});

    it("Should get reward in SDT", async function () {
        await network.provider.send("evm_increaseTime", [86400 * 2]); // 2 days
        await network.provider.send("evm_mine", []);
        await gauge.connect(holderSigner).getReward()
        const balance = await sdt.balanceOf(holderSigner._address)
        expect(balance).to.be.gt(0)
	});

    it("Should widraw from gauge", async function () {
        await gauge.connect(holderSigner).withdraw(parseEther("10"))
        const gaugeBalance = await sdav3CRV.balanceOf(gauge.address)
        expect(gaugeBalance).to.be.eq(0)
	});
});
