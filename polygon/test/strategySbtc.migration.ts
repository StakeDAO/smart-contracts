import {ethers, network} from 'hardhat';
import {expect} from 'chai';
import {BigNumber} from '@ethersproject/bignumber';
import {Contract} from '@ethersproject/contracts';
import {parseEther} from '@ethersproject/units';
import {JsonRpcSigner} from '@ethersproject/providers';

import Controller from '../abis/Controller.json';
import YVault from '../abis/YVault.json';
import ERC20 from '../abis/ERC20.json';
import ICurveGauge from '../abis/ICurveGauge.json'

const VAULT = '0x953Cf8f1f097c222015FFa32C7B9e3E96993b8c1';
const CONTROLLER = '0x91aE00aaC6eE0D7853C8F92710B641F68Cd945Df';
const GOVERNANCE = '0xb36a0671B3D49587236d7833B01E79798175875f';
const OLD_STRATEGY = '0x2fc878ad596939c36dd9f445ae0fab45a78a9830';

const CRV = '0x172370d5Cd63279eFa6d502DAB29171933a610AF';
const WANT = '0xf8a57c1d3b9629b77b6726a042ca48990a84fb49';

describe('StrategyBtcCurve', function () {
  let vault: Contract;
  let want: Contract;
  let crv: Contract;
  let controller: Contract;
  let strategy: Contract;
  let oldStrategy: Contract;
  let crvGauge: Contract;
  let governanceSigner: JsonRpcSigner;

  let initialBalance: BigNumber;

  before(async function () {
    // this.enableTimeouts(false);
    const [owner] = await ethers.getSigners();

    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [CONTROLLER]
    });

    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [GOVERNANCE]
    });

    const Strategy = await ethers.getContractFactory('StrategyBtcCurve');

    vault = await ethers.getContractAt(YVault, VAULT);
    controller = await ethers.getContractAt(Controller, CONTROLLER);
    want = await ethers.getContractAt(ERC20, WANT);
    crv = await ethers.getContractAt(ERC20, CRV);
    oldStrategy = await ethers.getContractAt('StrategyBtcCurve', OLD_STRATEGY);
    crvGauge = await ethers.getContractAt(ICurveGauge,'0x8D9649e50A0d1da8E939f800fB926cdE8f18B47D');
    strategy = await Strategy.deploy(CONTROLLER);

    governanceSigner = await ethers.provider.getSigner(GOVERNANCE);

    initialBalance = await vault.balance();

    await (
      await controller
        .connect(governanceSigner)
        .approveStrategy(WANT, strategy.address)
    ).wait();

    await (
      await controller
        .connect(governanceSigner)
        .setStrategy(WANT, strategy.address)
    ).wait();
  });

  it('All funds should be in vault', async function () {
    const vaultBalance = await want.balanceOf(vault.address);
    expect(vaultBalance.eq(initialBalance)).to.be.true;
  });

  it('Should send funds to strategy', async function () {
    await (await vault.earn()).wait();
    await (await vault.earn()).wait();
    await (await vault.earn()).wait();

    const strategyPoolBalance = await strategy.balanceOfPool();
    expect(strategyPoolBalance.gt(0)).to.be.true;
    const oldStrategyPoolBalance = await oldStrategy.balanceOfPool();
    
    expect(oldStrategyPoolBalance.eq(0)).to.be.true;

    // Testing old gauge award remains
		expect(await crvGauge.claimable_reward(oldStrategy.address,'0x47536F17F4fF30e64A96a7555826b8f9e66ec468')).to.eq(0)
		expect(await crvGauge.claimable_reward(oldStrategy.address,'0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7')).to.eq(0)
  });
});
