import {ethers, network} from 'hardhat';
import {expect} from 'chai';
import {BigNumber} from '@ethersproject/bignumber';
import {Contract} from '@ethersproject/contracts';
import {parseEther} from '@ethersproject/units';
import {JsonRpcSigner} from '@ethersproject/providers';

import Controller from '../abis/Controller.json';
import ERC20 from '../abis/ERC20.json';

const CONTROLLER = '0x29D3782825432255041Db2EAfCB7174f5273f08A';
const WANT = '0xA3D87FffcE63B53E0d54fAa1cc983B7eB0b74A9c';
const GOVERNANCE = '0xF930EBBd05eF8b25B1797b9b2109DDC9B0d43063';
const WANT_HOLDER = '0x995a09ed0b24Ee13FbfCFbe60cad2fB6281B479F';

const PROXY = '0xF34Ae3C7515511E29d8Afe321E67Bdf97a274f1A';
const RANDOM = '0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8';

const VE_CRV = '0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2';
const CURVE_VOTER = '0x52f541764E6e90eeBc5c21Ff570De0e2D63766B6';

const VEABI = [
  {
    name: 'locked',
    outputs: [
      {type: 'int128', name: 'amount'},
      {type: 'uint256', name: 'end'}
    ],
    inputs: [{type: 'address', name: 'arg0'}],
    stateMutability: 'view',
    type: 'function',
    gas: 3359
  }
];

describe('ConvexSeth', function () {
  let controller: Contract;
  let strategy: Contract;
  let vault: Contract;
  let want: Contract;
  let veCRV: Contract;
  let wantHolder: JsonRpcSigner;
  let governance: JsonRpcSigner;
  let controllerSigner: JsonRpcSigner;

  before(async function () {
    this.enableTimeouts(false);
    const [owner] = await ethers.getSigners();

    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [GOVERNANCE]
    });

    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [WANT_HOLDER]
    });

    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [CONTROLLER]
    });

    const Vault = await ethers.getContractFactory('Vault');
    const Strategy = await ethers.getContractFactory('StrategySEthConvex');

    governance = await ethers.provider.getSigner(GOVERNANCE);
    wantHolder = await ethers.provider.getSigner(WANT_HOLDER);
    controllerSigner = await ethers.provider.getSigner(CONTROLLER);

    strategy = await Strategy.deploy(CONTROLLER, PROXY);
    vault = await Vault.deploy(WANT, CONTROLLER, GOVERNANCE);

    controller = await ethers.getContractAt(Controller, CONTROLLER);

    want = await ethers.getContractAt(ERC20, WANT);
    veCRV = await ethers.getContractAt(VEABI, VE_CRV);

    const tx0 = await controller
      .connect(governance)
      .setVault(WANT, vault.address);

    console.log('setVault :', tx0.hash);
    await tx0.wait();

    const tx1 = await controller
      .connect(governance)
      .approveStrategy(WANT, strategy.address);

    console.log('approveStrategy :', tx1.hash);
    await tx1.wait();

    const tx2 = await controller
      .connect(governance)
      .setStrategy(WANT, strategy.address);

    console.log('setStrategy :', tx2.hash);
    await tx2.wait();

    /*
      SIMULATE INITIAL DEPOSIT IN THE VAULT
    */
    const holderBalance = await want.balanceOf(WANT_HOLDER);
    await (
      await want.connect(wantHolder).approve(vault.address, holderBalance)
    ).wait();

    await (await vault.connect(wantHolder).deposit(holderBalance)).wait();
  });

  it('All funds should be in vault', async function () {
    const vaultBalance = await vault.balance();
    const vaulteCRVBalance = await want.balanceOf(vault.address);

    console.log({
      vaultBalance: vaultBalance.toString(),
      vaulteCRVBalance: vaulteCRVBalance.toString()
    });

    expect(vaultBalance.eq(vaulteCRVBalance)).to.be.true;
  });

  it('should deposit 95% of vault balance in convex sEth', async function () {
    this.enableTimeouts(false);
    const vaultBalance = await vault.balance();

    console.log({
      vaultBalance: vaultBalance.toString()
    });

    const tx = await vault.earn();
    await tx.wait();

    const balance = await strategy.balanceOf();
    const amountExpected = vaultBalance.mul(95).div(100);

    console.log({
      balance: balance.toString(),
      amountExpected: amountExpected.toString()
    });

    expect(balance.eq(amountExpected)).to.be.true;
  });

  it('should lock CRV and ensure we have more LP in baseRewardPool', async function () {
    this.enableTimeouts(false);

    const {amount: veCRVBalanceBefore} = await veCRV.locked(CURVE_VOTER);

    ethers.provider.send('evm_increaseTime', [3600]);
    ethers.provider.send('evm_mine', []);

    const balanceBefore = await strategy.balanceOfPool();
    const tx = await strategy.harvest(100, 100, 100);
    await tx.wait();
    const balanceAfter = await strategy.balanceOfPool();

    const {amount: veCRVBalanceAfter} = await veCRV.locked(CURVE_VOTER);
    const hasLockedCRV = veCRVBalanceAfter.gt(veCRVBalanceBefore);

    expect(hasLockedCRV).to.be.true; // ensure that we lock CRV
    expect(balanceAfter.gt(balanceBefore)).to.be.true; //
  });

  it('should harvest', async function () {
    this.enableTimeouts(false);

    ethers.provider.send('evm_increaseTime', [3600 * 24]);
    ethers.provider.send('evm_mine', []);

    const balanceBefore = await strategy.balanceOf();
    const tx = await strategy.harvest(100, 100, 100);
    await tx.wait();
    const balanceAfter = await strategy.balanceOf();

    expect(balanceAfter.gt(balanceBefore)).to.be.true;
  });

  it('should withdraw some for the user', async function () {
    this.enableTimeouts(false);
    const balanceBefore = await strategy.balanceOf();
    const amountDeposited = await want.balanceOf(WANT_HOLDER);

    const tx0 = await want
      .connect(wantHolder)
      .approve(vault.address, amountDeposited);

    await tx0.wait();

    const tx1 = await vault.connect(wantHolder).deposit(amountDeposited);
    await tx1.wait();

    // triple earn to leave close to nothing in vault (5% always stay with earn)
    const tx2 = await vault.earn();
    await tx2.wait();
    const tx2b = await vault.earn();
    await tx2b.wait();
    const tx2c = await vault.earn();
    await tx2c.wait();

    //available in the vault (95%) that can be sent to strat
    //const vaultAvailableAfterEarn = await vault.available();
    const vaultAvailableAfterEarn = await want.balanceOf(vault.address);

    const balanceAfterEarn = await strategy.balanceOf();

    const sdBalance = await vault.balanceOf(WANT_HOLDER);
    const pricePerShare = await vault.getPricePerFullShare();

    const getInWant = (am: BigNumber): any => {
      return am
        .mul(pricePerShare)
        .div(BigNumber.from(1).mul(BigNumber.from(10).pow(18)));
    };

    const withdrawAmount = sdBalance.div(4);
    const withdrawAmountWant = getInWant(withdrawAmount);

    const userWantBalanceBefore = await want.balanceOf(WANT_HOLDER);

    const tx3 = await vault.connect(wantHolder).withdraw(withdrawAmount);
    await tx3.wait();

    const balanceAfterWithdraw = await strategy.balanceOf();
    const userWantBalanceAfter = await want.balanceOf(WANT_HOLDER);

    const expectedWithdrawFromStrategy = withdrawAmountWant.sub(
      vaultAvailableAfterEarn
    );

    const balanceDifference = balanceAfterEarn.sub(balanceAfterWithdraw);

    // 0.5% user withdrawal paid fees
    const withdrawalFee = withdrawAmountWant
      .sub(vaultAvailableAfterEarn)
      .mul(5)
      .div(1000);

    const expectedUserBalanceWantAfter = withdrawAmountWant
      .sub(withdrawalFee)
      .add(userWantBalanceBefore);
  });

  it('should withdraw all', async function () {
    this.enableTimeouts(false);

    const balanceBefore = await strategy.balanceOf();
    const vaultBalanceBefore = await want.balanceOf(vault.address);

    const tx1 = await controller
      .connect(governance)
      .approveStrategy(WANT, RANDOM);

    await tx1.wait();

    // replace strat by random strat
    const tx2 = await controller.connect(governance).setStrategy(WANT, RANDOM);

    await tx2.wait();

    const balanceAfter = await strategy.balanceOf();
    const vaultBalanceAfter = await want.balanceOf(vault.address);

    expect(balanceBefore.gt(0)).to.be.true;
    expect(balanceAfter.eq(0)).to.be.true;
    expect(vaultBalanceAfter.gt(vaultBalanceBefore)).to.be.true;
    expect(vaultBalanceBefore.add(balanceBefore).eq(vaultBalanceAfter)).to.be
      .true;
  });
});
