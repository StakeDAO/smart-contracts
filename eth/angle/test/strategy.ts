import { ethers, network } from "hardhat";
import { expect } from "chai";
import { BigNumber } from "@ethersproject/bignumber";
import { Contract, ContractTransaction } from "@ethersproject/contracts";
import { parseEther } from "@ethersproject/units";
import { JsonRpcSigner } from "@ethersproject/providers";

import Controller from "./fixtures/Controller.json";
import ERC20 from "./fixtures/ERC20.json";
import { parse } from "path/posix";

const CONTROLLER = "0x29D3782825432255041Db2EAfCB7174f5273f08A";
const CONTROLLER_ADMIN = "0xf930ebbd05ef8b25b1797b9b2109ddc9b0d43063";
const WANT = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"; // USDC
const POOL_MANAGER = "0xe9f183FC656656f1F17af1F2b0dF79b8fF9ad8eD";
const STABLE_MASTER = "0x5adDc89785D75C86aB939E9e15bfBBb7Fc086A87";
const GOVERNANCE = "0xF930EBBd05eF8b25B1797b9b2109DDC9B0d43063";
const WANT_HOLDER = "0x41339d9825963515e5705df8d3b0ea98105ebb1c"; // USDC holder
const SANUSDC_EUR = "0x9C215206Da4bf108aE5aEEf9dA7caD3352A36Dad";
const ANGLE = "0x31429d1856aD1377A8A0079410B297e1a9e214c2";
const SDT = "0x73968b9a57c6E53d41345FD57a6E6ae27d6CDB2F";
const SDT_HOLDER = "0x026B748689c3a4363ca044A323D5F405fe16a750";
const AGEUR = "0x1a7e4e63778B4f12a199C062f3eFdD288afCBce8";
const PROXY = "0xF34Ae3C7515511E29d8Afe321E67Bdf97a274f1A";
const STAKING_REWARDS = "0x2Fa1255383364F6e17Be6A6aC7A56C9aCD6850a3";

describe("ANGLE USDC strat", function () {
  let controller: Contract;
  let strategy: Contract;
  let strategyNew: Contract;
  let vault: Contract;
  let want: Contract;
  let angle: Contract;
  let sdt: Contract;
  let sanLP: Contract;
  let stableMaster: Contract;
  let controllerAdmin: JsonRpcSigner;
  let wantHolder: JsonRpcSigner;
  let sdtHolder: JsonRpcSigner;
  let governance: JsonRpcSigner;
  let controllerSigner: JsonRpcSigner;
  let ageur: Contract;
  let gauge: Contract;
  let stakingRewards: Contract;

  before(async function () {
    this.enableTimeouts(false);
    const [owner] = await ethers.getSigners();

    await network.provider.request({
      method: "hardhat_impersonateAccount",
      params: [GOVERNANCE]
    });

    await network.provider.request({
      method: "hardhat_impersonateAccount",
      params: [WANT_HOLDER]
    });

    await network.provider.request({
      method: "hardhat_impersonateAccount",
      params: [CONTROLLER]
    });

    await network.provider.request({
      method: "hardhat_impersonateAccount",
      params: [SDT_HOLDER]
    });

    await network.provider.request({
      method: "hardhat_impersonateAccount",
      params: [CONTROLLER_ADMIN]
    });

    const Strategy = await ethers.getContractFactory("StrategyAngleStakeDao");
    const Vault = await ethers.getContractFactory("Vault");
    const Gauge = await ethers.getContractFactory("GaugeMultiRewards");

    governance = await ethers.provider.getSigner(GOVERNANCE);
    wantHolder = await ethers.provider.getSigner(WANT_HOLDER);
    sdtHolder = await ethers.provider.getSigner(SDT_HOLDER);
    controllerAdmin = await ethers.provider.getSigner(CONTROLLER_ADMIN);
    controllerSigner = await ethers.provider.getSigner(CONTROLLER);
    controller = await ethers.getContractAt(Controller, CONTROLLER);
    vault = await Vault.deploy(WANT, controller.address);
    stableMaster = await ethers.getContractAt("IStableMaster", STABLE_MASTER);
    stakingRewards = await ethers.getContractAt("IStakingRewards", STAKING_REWARDS);
    ageur = await ethers.getContractAt("IERC20", AGEUR);
    gauge = await Gauge.deploy(vault.address);
    strategy = await Strategy.deploy(CONTROLLER, WANT, gauge.address);
    strategyNew = await Strategy.deploy(CONTROLLER, WANT, gauge.address);
    want = await ethers.getContractAt(ERC20, WANT);
    sanLP = await ethers.getContractAt(ERC20, SANUSDC_EUR);
    angle = await ethers.getContractAt(ERC20, ANGLE);
    sdt = await ethers.getContractAt(ERC20, SDT);
    await gauge.addReward(ANGLE, strategy.address, 86400 * 3);

    const tx1 = await controller.connect(governance).approveStrategy(WANT, strategy.address);

    await tx1.wait();

    const tx2 = await controller.connect(governance).setStrategy(WANT, strategy.address);

    await tx2.wait();

    const tx3 = await controller.connect(governance).setVault(WANT, vault.address);
    await tx3.wait();
    await ageur.connect(wantHolder).approve(stableMaster.address, ethers.constants.MaxUint256);
    await want.connect(wantHolder).approve(vault.address, ethers.constants.MaxUint256);
  });

  it("User should not deposit before gauge has been set", async function () {
    this.enableTimeouts(false);
    const amount = BigNumber.from(10).pow(6).mul(20000); // 20k USDC

    await expect(vault.connect(wantHolder).deposit(amount)).to.be.revertedWith("Gauge not yet initialized");
  });
  it("User should be able to deposit and withdraw immediately", async function () {
    this.enableTimeouts(false);
    await vault.setGauge(gauge.address);
    const usdcBalance = await want.balanceOf(wantHolder._address);
    const amount = BigNumber.from(10).pow(6).mul(20000); // 20k USDC
    await vault.connect(wantHolder).deposit(amount);
    const usdcBalanceAfterDeposit = await want.balanceOf(wantHolder._address);
    const sanLpBalance = await gauge.balanceOf(wantHolder._address);
    await vault.connect(wantHolder).withdraw(sanLpBalance);
    const usdcBalanceAfterWithdraw = await want.balanceOf(wantHolder._address);
    expect(usdcBalance).to.be.gt(0);
    expect(usdcBalanceAfterDeposit).to.be.lt(usdcBalance);
    expect(usdcBalanceAfterWithdraw).to.be.gt(usdcBalance);
  });
  it("User should deposit USDC in vault", async function () {
    this.enableTimeouts(false);
    const amount = BigNumber.from(10).pow(6).mul(20000); // 20k USDC
    const sanLpBalanceBeforeDeposit = await gauge.balanceOf(wantHolder._address);
    await vault.connect(wantHolder).deposit(amount);
    const sanLpBalanceAfterDeposit = await gauge.balanceOf(wantHolder._address);
    expect(sanLpBalanceAfterDeposit).to.be.gt(sanLpBalanceBeforeDeposit); // make sure it staked
  });

  it("it should withdraw the partial amount of the staked amount", async function () {
    this.enableTimeouts(false);
    const withDrawAmountWithoutProfit = BigNumber.from(10).pow(6).mul(20000).mul(20).div(100);
    const usdcBalanceOfUser = await want.balanceOf(wantHolder._address);
    const sanLpBalance = (await gauge.balanceOf(wantHolder._address)).mul(20).div(100);
    await vault.connect(wantHolder).withdraw(sanLpBalance);
    const usdcBalanceOfUserAfterWithdraw = await want.balanceOf(wantHolder._address);
    expect(usdcBalanceOfUserAfterWithdraw).to.be.gt(usdcBalanceOfUser); // make sure user get the usdc
    expect(usdcBalanceOfUserAfterWithdraw.sub(usdcBalanceOfUser)).to.be.gt(withDrawAmountWithoutProfit); // make sure user gets profit
  });

  it("Should harvest", async function () {
    this.enableTimeouts(false);
    await vault.earn();
    await network.provider.send("evm_increaseTime", [86400 * 5]);
    await network.provider.send("evm_mine", []);
    await strategy.harvest();
    const angleFarmed = await angle.balanceOf(gauge.address);
    expect(angleFarmed).to.be.gt(0);
  });

  it("Should get ANGLE reward from gauge, called by another address", async function () {
    this.enableTimeouts(false);

    await gauge.connect(governance).getRewardFor(wantHolder._address);
    const angleFarmed = await angle.balanceOf(wantHolder._address);
    expect(angleFarmed).to.be.gt(0);
  });

  it("Should add new reward and notify it", async function () {
    this.enableTimeouts(false);
    await gauge.addReward(SDT, sdtHolder._address, 86400 * 3);
    await sdt.connect(sdtHolder).approve(gauge.address, parseEther("100"));
    await gauge.connect(sdtHolder).notifyRewardAmount(SDT, parseEther("100"));
    await network.provider.send("evm_increaseTime", [86400 * 2]);
    await network.provider.send("evm_mine", []);
  });

  it("Should migrate to the new angle staking contract", async function () {
    this.enableTimeouts(false);
    const balanceInOldStaking = await strategy.balanceOfPool();
    await strategy.setStaking(strategy.staking());
    const balanceInNewStaking = await strategy.balanceOfPool();
    expect(balanceInOldStaking).to.be.eq(balanceInNewStaking);
  });

  it("Should deploy new strategy", async function () {
    this.enableTimeouts(false);
    await controller.connect(governance).approveStrategy(WANT, strategyNew.address);
    // set new strategy, it will call withdrawAll()
    await controller.connect(governance).setStrategy(WANT, strategyNew.address);
    const sanLPAmount = await sanLP.balanceOf(vault.address);
    expect(sanLPAmount).to.be.gt(0);
    // it sends again funds to the new strategy
    await vault.earn();
  });

  it("it should withdraw their usdc along with profits", async function () {
    this.enableTimeouts(false);
    const withDrawAmountWithoutProfit = BigNumber.from(10).pow(6).mul(20000).mul(80).div(100);
    const rateBefore = await stableMaster.collateralMap(POOL_MANAGER);
    await manipulateExchangeRate();
    const rateAfter = await stableMaster.collateralMap(POOL_MANAGER);
    const usdcBalanceBeforeWithdraw = await want.balanceOf(wantHolder._address);
    const sanLpBalance = await gauge.balanceOf(wantHolder._address);
    await vault.connect(wantHolder).withdraw(sanLpBalance);
    const usdcBalanceAfterWithdraw = await want.balanceOf(wantHolder._address);
    const sanLpBalanceAfterWithdraw = await gauge.balanceOf(wantHolder._address);
    expect(rateAfter[5]).to.be.gt(rateBefore[5]);
    expect(sanLpBalanceAfterWithdraw).to.be.equal(0);
    expect(usdcBalanceAfterWithdraw.sub(usdcBalanceBeforeWithdraw)).to.be.gt(withDrawAmountWithoutProfit);
  });

  it("Should get ANGLE and SDT reward after the whole withdraw", async function () {
    this.enableTimeouts(false);
    const sanLpBalance = await gauge.balanceOf(wantHolder._address);
    expect(sanLpBalance).to.be.equal(0);
    const angleBefore = await angle.balanceOf(wantHolder._address);
    const sdtBefore = await sdt.balanceOf(wantHolder._address);
    await gauge.connect(wantHolder).getRewardFor(wantHolder._address);
    const angleAfter = await angle.balanceOf(wantHolder._address);
    const sdtAfter = await sdt.balanceOf(wantHolder._address);
    expect(angleAfter).to.be.gt(angleBefore);
    expect(sdtAfter).to.be.gt(sdtBefore);
  });

  it("After call earn lp tokens should staked to the angle staking contract", async function () {
    this.enableTimeouts(false);
    const stakedAmountInAngle = await stakingRewards.balanceOf(strategyNew.address);
    const amount = BigNumber.from(10).pow(6).mul(20000); // 20k USDC
    await vault.connect(wantHolder).deposit(amount);
    await vault.earn();
    const stakedAmountInAngleAfterEarn = await stakingRewards.balanceOf(strategyNew.address);
    expect(stakedAmountInAngle).to.be.equal(0);
    expect(stakedAmountInAngleAfterEarn).to.be.gt(stakedAmountInAngle);
  });

  it("Should not rescue sanLP when the vault is empty", async function () {
    this.enableTimeouts(false);
    await expect(vault.connect(sdtHolder).withdrawRescue()).to.be.revertedWith("Cannot withdraw 0");
  });

  it("User should rescue sanLP from vault", async function () {
    // it calls directly withdrawAll() from the controller
    await controller.connect(governance).withdrawAll(WANT);
    const sanLPAmount = await sanLP.balanceOf(vault.address);
    expect(sanLPAmount).to.be.gt(0);
    const amountBefore = await sanLP.balanceOf(wantHolder._address);
    await vault.connect(wantHolder).withdrawRescue();
    const amountAfter = await sanLP.balanceOf(wantHolder._address);
    const amountRescued = amountAfter.sub(amountBefore);
    expect(amountRescued).to.be.gt(0);
    const amountLeftInVault = await sanLP.balanceOf(vault.address);
    expect(amountLeftInVault).to.be.eq(0);
  });

  async function manipulateExchangeRate() {
    const amount = BigNumber.from(10).pow(6).mul(100000);
    await want.connect(wantHolder).approve(stableMaster.address, amount);
    await stableMaster.connect(wantHolder).mint(amount, wantHolder._address, POOL_MANAGER, 0); // make some ageur minting to increase LP token reward rate
    const agEUrBal = await ageur.balanceOf(wantHolder._address);
    await stableMaster.connect(wantHolder).burn(agEUrBal, wantHolder._address, wantHolder._address, POOL_MANAGER, 0);
  }
});
