import {ethers, network} from 'hardhat';
import {expect} from 'chai';
import {BigNumber} from '@ethersproject/bignumber';
import {Contract} from '@ethersproject/contracts';
import {parseEther} from '@ethersproject/units';
import {JsonRpcSigner} from '@ethersproject/providers';

import Controller from '../abis/Controller.json';
import YVault from '../abis/YVault.json';
import ERC20 from '../abis/ERC20.json';

const VAULT = '0x7d60F21072b585351dFd5E8b17109458D97ec120';
const CONTROLLER = '0x91aE00aaC6eE0D7853C8F92710B641F68Cd945Df';
const GOVERNANCE = '0xb36a0671B3D49587236d7833B01E79798175875f';
const OLD_STRATEGY = '0x552DAd974da30D67f25BE444991E22CbaE357851';

const CRV = '0x172370d5Cd63279eFa6d502DAB29171933a610AF';
const WANT = '0xE7a24EF0C5e95Ffb0f6684b813A78F2a3AD7D171'; // am3CRV

describe('StrategyAm3Crv', function () {
  let vault: Contract;
  let want: Contract;
  let crv: Contract;
  let controller: Contract;
  let strategy: Contract;
  let oldStrategy: Contract;
  let governanceSigner: JsonRpcSigner;

  let initialBalance: BigNumber;

  before(async function () {
    this.enableTimeouts(false);
    const [owner] = await ethers.getSigners();

    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [CONTROLLER]
    });

    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [GOVERNANCE]
    });

    const Strategy = await ethers.getContractFactory('StrategyAm3Crv');

    vault = await ethers.getContractAt(YVault, VAULT);
    controller = await ethers.getContractAt(Controller, CONTROLLER);
    want = await ethers.getContractAt(ERC20, WANT);
    crv = await ethers.getContractAt(ERC20, CRV);
    oldStrategy = await ethers.getContractAt('StrategyAm3Crv', OLD_STRATEGY);

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
  });
});
