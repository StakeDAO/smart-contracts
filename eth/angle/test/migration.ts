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
const WANT_HOLDER = "0x0DAFB4114762bDf555d9c6BDa02f4ffEc89964ec"; // USDC holder
const SANUSDC_EUR = "0x9C215206Da4bf108aE5aEEf9dA7caD3352A36Dad";
const ANGLE = "0x31429d1856aD1377A8A0079410B297e1a9e214c2";
const SDT = "0x73968b9a57c6E53d41345FD57a6E6ae27d6CDB2F";
const SDT_HOLDER = "0x026B748689c3a4363ca044A323D5F405fe16a750";
const AGEUR = "0x1a7e4e63778B4f12a199C062f3eFdD288afCBce8";
const PROXY = "0xF34Ae3C7515511E29d8Afe321E67Bdf97a274f1A";
const STAKING_REWARDS = "0x2Fa1255383364F6e17Be6A6aC7A56C9aCD6850a3";
const STAKEDAO_DEPLOYER = "0xb36a0671b3d49587236d7833b01e79798175875f";
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
  let liquidityGauge: Contract;
  let vaultGovernance: JsonRpcSigner;

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
    await network.provider.request({
      method: "hardhat_impersonateAccount",
      params: [STAKEDAO_DEPLOYER]
    });
    await network.provider.send("hardhat_setBalance", [STAKEDAO_DEPLOYER, "0x56BC75E2D63100000"]);
    await network.provider.send("hardhat_setBalance", [WANT_HOLDER, "0x56BC75E2D63100000"]);
    governance = await ethers.provider.getSigner(GOVERNANCE);
    wantHolder = await ethers.provider.getSigner(WANT_HOLDER);
    vaultGovernance = await ethers.provider.getSigner(STAKEDAO_DEPLOYER);
    sdtHolder = await ethers.provider.getSigner(SDT_HOLDER);
    controllerAdmin = await ethers.provider.getSigner(CONTROLLER_ADMIN);
    controllerSigner = await ethers.provider.getSigner(CONTROLLER);
    controller = await ethers.getContractAt(Controller, CONTROLLER);
    vault = await ethers.getContractAt("Vault", "0xf3c2bdfCCb75CAFdA3D69d807c336bede956563f");
    stableMaster = await ethers.getContractAt("IStableMaster", STABLE_MASTER);
    stakingRewards = await ethers.getContractAt("IStakingRewards", STAKING_REWARDS);
    ageur = await ethers.getContractAt("IERC20", AGEUR);
    gauge = await ethers.getContractAt("GaugeMultiRewards", "0x3c310fc54c0534dc3c45312934508722284352d1");
    strategy = await ethers.getContractAt("StrategyAngleStakeDao", "0x9eEF1244AE7aeeDeAa3Df2a91B63eAABC4Fce257");
    liquidityGauge = await ethers.getContractAt("ILiquidityGauge", "0x51fE22abAF4a26631b2913E417c0560D547797a7");
    want = await ethers.getContractAt(ERC20, WANT);
    sanLP = await ethers.getContractAt(ERC20, SANUSDC_EUR);
    angle = await ethers.getContractAt(ERC20, ANGLE);
    sdt = await ethers.getContractAt(ERC20, SDT);

    await ageur.connect(wantHolder).approve(stableMaster.address, ethers.constants.MaxUint256);
    await want.connect(wantHolder).approve(vault.address, ethers.constants.MaxUint256);
  });

  it("it should migrate the strat", async function () {
    this.enableTimeouts(false);
    const newStratFactory = await ethers.getContractFactory("NewStrategyAngleStakeDao");
    strategyNew = await newStratFactory.deploy(controller.address, want.address, gauge.address);
    const sanLpBalanceOfVaultBeforeWithdrawAll = await sanLP.balanceOf(vault.address);
    await (await controller.connect(governance).approveStrategy(want.address, strategyNew.address)).wait();
    await (await controller.connect(governance).setStrategy(want.address, strategyNew.address)).wait();
    const sanLpBalanceOfVaultAfterWithdrawAll = await sanLP.balanceOf(vault.address);
    expect(sanLpBalanceOfVaultAfterWithdrawAll).to.be.gt(sanLpBalanceOfVaultBeforeWithdrawAll);
  });

  it("it should stake to the new staking contract", async function () {
    this.enableTimeouts(false);
    const stakedAmountBeforeEarn = await liquidityGauge.balanceOf(strategyNew.address);
    await (await vault.connect(vaultGovernance).earn()).wait();
    const stakedAmountAfterEarn = await liquidityGauge.balanceOf(strategyNew.address);
    expect(stakedAmountBeforeEarn).to.be.equal(0);
    expect(stakedAmountAfterEarn).to.be.gt(stakedAmountBeforeEarn);
  });

  it("User should deposit USDC in vault", async function () {
    this.enableTimeouts(false);
    const amount = BigNumber.from(10).pow(6).mul(20000); // 20k USDC
    const sanLpBalanceBeforeDeposit = await gauge.balanceOf(wantHolder._address);
    await vault.connect(wantHolder).deposit(amount);
    const sanLpBalanceAfterDeposit = await gauge.balanceOf(wantHolder._address);
    expect(sanLpBalanceAfterDeposit).to.be.gt(sanLpBalanceBeforeDeposit); // make sure it staked
  });
  it("User should be able to withdraw after earn", async function () {
    this.enableTimeouts(false);
    const stakedAmountBeforeEarn = await liquidityGauge.balanceOf(strategyNew.address);
    await (await vault.connect(vaultGovernance).earn()).wait();
    const stakedAmountAfterEarn = await liquidityGauge.balanceOf(strategyNew.address);
    const sanLpBalanceBeforeWithdraw = await gauge.balanceOf(wantHolder._address);
    await vault.connect(wantHolder).withdraw(sanLpBalanceBeforeWithdraw);
    const sanLpBalanceAfterWithdraw = await gauge.balanceOf(wantHolder._address);
    expect(stakedAmountBeforeEarn).to.be.gt(0);
    expect(stakedAmountAfterEarn).to.be.gt(stakedAmountBeforeEarn);
    expect(sanLpBalanceBeforeWithdraw).to.be.gt(0);
    expect(sanLpBalanceAfterWithdraw).to.be.eq(0);
  });
});
