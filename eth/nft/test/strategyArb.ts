import { ethers, network } from 'hardhat'
import { expect } from 'chai'
import { Contract } from '@ethersproject/contracts'
import { parseEther } from '@ethersproject/units'
import { JsonRpcSigner } from '@ethersproject/providers'

import ERC20 from '../abis/ERC20.json'
import Palace from '../abis/Palace.json'
import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/signers'

const SDT = '0x73968b9a57c6e53d41345fd57a6e6ae27d6cdb2f'
const sdFRAX3CRV = '0x5af15DA84A4a6EDf2d9FA6720De921E1026E37b7'
const PALACE = '0x221738f73fA4bfCA91918E77d112b87D918c751f'

const SDTWHALE = '0xc5d3d004a223299c4f95bb702534c14a32e8778c'
const sdFRAX3CRVWHALE = '0x285e4f019a531e20f673b634d31922d408970798'
const DEPLOYER = '0xb36a0671B3D49587236d7833B01E79798175875f'

const DUMMYUSERC = '0x80d9BC4B2B21C69ba2B7ED92882fF79069Ea7e13'
const PALACE_WHALE = '0x6d75fFBfFd1e63e5072F0Ffbf6c4EeFa16043967'

const commonLimit = parseEther('1000')
const rareLimit = parseEther('5000')
const uniqueLimit = parseEther('10000')

describe('Arb Strategy', function () {
  let stakingRewards: Contract
  let sdt: Contract
  let sdFRAX3CRVContract: Contract
  let stratAccessNFTContract: Contract
  let palace: Contract
  let sdtWhaleSigner: JsonRpcSigner
  let sdFrax3CRVWhaleSigner: JsonRpcSigner
  let baseOwner: SignerWithAddress
  let deployerSigner: JsonRpcSigner
  let palaceWhaleSigner: JsonRpcSigner
  let userC: JsonRpcSigner

  before(async function () {
    this.enableTimeouts(false)
    const [owner] = await ethers.getSigners()
    baseOwner = owner
    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [SDTWHALE],
    })

    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [sdFRAX3CRVWHALE],
    })

    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [DEPLOYER],
    })

    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [DUMMYUSERC],
    })

    await network.provider.request({
      method: 'hardhat_impersonateAccount',
      params: [PALACE_WHALE],
    })

    sdt = await ethers.getContractAt(ERC20, SDT)
    palace = await ethers.getContractAt(Palace, PALACE)
    sdFRAX3CRVContract = await ethers.getContractAt(ERC20, sdFRAX3CRV)
    sdtWhaleSigner = await ethers.provider.getSigner(SDTWHALE)
    sdFrax3CRVWhaleSigner = await ethers.provider.getSigner(sdFRAX3CRVWHALE)
    deployerSigner = await ethers.provider.getSigner(DEPLOYER)
    palaceWhaleSigner = await ethers.provider.getSigner(PALACE_WHALE)
    userC = await ethers.provider.getSigner(DUMMYUSERC)

    await owner.sendTransaction({
      to: DEPLOYER,
      value: parseEther('100').toHexString(),
    })

    const StratAccessNFT = await ethers.getContractFactory('StakeDaoNFT_V2')
    stratAccessNFTContract = await StratAccessNFT.deploy(
      '0xa5409ec958C83C3f309868babACA7c86DCB077c1',
    )

    const temp = await owner.sendTransaction({
      to: SDTWHALE,
      value: parseEther('100').toHexString(),
    })

    await owner.sendTransaction({
      to: sdFRAX3CRVWHALE,
      value: parseEther('100').toHexString(),
    })

    await owner.sendTransaction({
      to: DUMMYUSERC,
      value: parseEther('100').toHexString(),
    })

    await sdt
      .connect(sdtWhaleSigner)
      .transfer(owner.getAddress(), parseEther('10000'))
    await sdt.connect(sdtWhaleSigner).transfer(DUMMYUSERC, parseEther('320'))
    await sdFRAX3CRVContract
      .connect(sdFrax3CRVWhaleSigner)
      .transfer(deployerSigner.getAddress(), parseEther('900'))

    await sdt.connect(sdtWhaleSigner).transfer(PALACE_WHALE, parseEther('5000'))

    // await sdFRAX3CRVContract
    //   .connect(sdFrax3CRVWhaleSigner)
    //   .transfer(baseOwner.address, parseEther('100'))
    await stratAccessNFTContract.create(1, 1, 'yello', '0x')
    await stratAccessNFTContract.create(1, 1, 'yello', '0x')
    await stratAccessNFTContract.create(1, 1, 'yello', '0x')

    for (let index = 0; index < 109; index++) {
      await stratAccessNFTContract.create(1, 0, 'yello', '0x')
    }

    await stratAccessNFTContract.addMinter(palace.address)

    await palace.connect(deployerSigner).setNFT(stratAccessNFTContract.address)
    // deployer adding Cards (registering NFTs)
    await palace.connect(deployerSigner).addCard(230, parseEther('46000'))
    // then need a test wherein one of the palace holders (who has more than 48000 points earned in this case)
    // is able to mint from palace

    await stratAccessNFTContract.safeTransferFrom(
      owner.getAddress(),
      SDTWHALE,
      224,
      '1',
      '0x',
    )

    await stratAccessNFTContract.safeTransferFrom(
      owner.getAddress(),
      DUMMYUSERC,
      225,
      '1',
      '0x',
    )
  })

  async function InitializeStakingRewards() {
    const StakingRewards = await ethers.getContractFactory('DarkParadise')
    stakingRewards = await StakingRewards.connect(deployerSigner).deploy(
      DEPLOYER,
      sdFRAX3CRV,
      SDT,
      stratAccessNFTContract.address,
    )
    await stratAccessNFTContract.addStrategy(stakingRewards.address)
    await stakingRewards
      .connect(deployerSigner)
      .setRewardsDistribution(DEPLOYER)
  }

  describe('NFT Test', async () => {
    it('Batch', async function () {
      var max = []
      var initSupp = []
      var uri = []
      for (let index = 0; index < 223; index++) {
        max[index] = index
        initSupp[index] = index
        uri[index] = ''
      }
      await stratAccessNFTContract.batchCreate(max, initSupp, uri, '0x')

      for (let index = 223; index < 445; index++) {
        expect(await stratAccessNFTContract.creators(index)).to.equal(
          baseOwner.address,
        )
      }
    })
  })

  describe('Staking', async () => {
    beforeEach(async function () {
      await InitializeStakingRewards()
    })

    it('User could not stake with any nft', async function () {
      await sdt.approve(stakingRewards.address, parseEther('1'))
      await expect(
        stakingRewards['stake(uint256,uint256)'](parseEther('1'), 1),
      ).revertedWith('Invalid nft')
    })

    it('User could stake only if they have nft', async function () {
      await sdt.approve(stakingRewards.address, parseEther('1'))

      await stakingRewards
        .connect(baseOwner)
        ['stake(uint256,uint256)'](parseEther('1'), 223)
      expect(await sdt.balanceOf(stakingRewards.address)).to.equal(
        parseEther('1'),
      )
    })

    it('User could not transfer a NFT that is staked in a strategy', async function () {
      await sdt.approve(stakingRewards.address, parseEther('1'))
      await stakingRewards
        .connect(baseOwner)
        ['stake(uint256,uint256)'](parseEther('1'), 223)

      await expect(
        stratAccessNFTContract.safeTransferFrom(
          baseOwner.getAddress(),
          SDTWHALE,
          223,
          '1',
          '0x',
        ),
      ).revertedWith('StakeDaoNFT_V2: NFT being used in strategy')
    })

    it('User could not stake if they do not have nft', async function () {
      await sdt
        .connect(sdtWhaleSigner)
        .approve(stakingRewards.address, parseEther('1'))
      await expect(
        stakingRewards
          .connect(sdtWhaleSigner)
          ['stake(uint256,uint256)'](parseEther('1'), 225),
      ).revertedWith('StakeDaoNFT_V2: user account doesnt have NFT')
    })

    it('User should be able to deposit the amount their NFT permits', async function () {
      await sdt.approve(stakingRewards.address, commonLimit)
      expect(await sdt.balanceOf(baseOwner.getAddress())).to.equal(
        parseEther('9998'),
      )
      await expect(
        stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](commonLimit, 223),
      ).emit(stakingRewards, 'Staked')
      expect(await sdt.balanceOf(stakingRewards.address)).to.equal(commonLimit)
      expect(await sdt.balanceOf(baseOwner.getAddress())).to.equal(
        parseEther('8998'),
      )
    })

    it('User should not be able to deposit more than the amount their NFT permits', async function () {
      await sdt.approve(stakingRewards.address, uniqueLimit)
      await expect(
        stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](uniqueLimit, 223),
      ).revertedWith('Crossing limit')
    })

    it('Palace whale is able to mint from palace', async function () {
      await palace.connect(palaceWhaleSigner).redeem(230)
      const nftBal = await stratAccessNFTContract.balanceOf(PALACE_WHALE, 230)
      await expect(nftBal).to.equal(1)
    })
  })

  describe('Withdrawing', async () => {
    beforeEach(async function () {
      await InitializeStakingRewards()
      await sdt.approve(stakingRewards.address, parseEther('1'))
      await stakingRewards
        .connect(baseOwner)
        ['stake(uint256,uint256)'](parseEther('1'), 223)
    })

    it('User could withdraw complete amount', async function () {
      expect(await sdt.balanceOf(baseOwner.getAddress())).to.equal(
        parseEther('8997'),
      )
      await stakingRewards.connect(baseOwner).exit()
      expect(await sdt.balanceOf(stakingRewards.address)).to.equal(
        parseEther('0'),
      )
      expect(await sdt.balanceOf(baseOwner.getAddress())).to.equal(
        parseEther('8998'),
      )
    })

    it('User could withdraw partial amount', async function () {
      expect(await sdt.balanceOf(baseOwner.getAddress())).to.equal(
        parseEther('8997'),
      )
      await stakingRewards.connect(baseOwner).withdraw(parseEther('0.5'))
      expect(await sdt.balanceOf(stakingRewards.address)).to.equal(
        parseEther('0.5'),
      )
      expect(await sdt.balanceOf(baseOwner.getAddress())).to.equal(
        parseEther('8997.5'),
      )
    })

    it('User cannot withdraw amount more than they have staked', async function () {
      await expect(stakingRewards.withdraw(parseEther('2'))).revertedWith(
        'SafeMath: subtraction overflow',
      )
    })

    it('User cannot withdraw if they dont have any amount staked', async function () {
      await expect(
        stakingRewards.connect(sdtWhaleSigner).withdraw(parseEther('1')),
      ).revertedWith('SafeMath: subtraction overflow')
    })
  })

  describe('Rewards', async () => {
    describe('Deposit', async () => {
      beforeEach(async function () {
        await InitializeStakingRewards()
        await sdFRAX3CRVContract
          .connect(deployerSigner)
          .approve(stakingRewards.address, parseEther('10'))
      })

      it('Only authorized user could deposit rewards', async function () {
        await stakingRewards
          .connect(deployerSigner)
          .notifyRewardAmount(parseEther('1'), parseEther('1'))
      })

      it('Unauthorized user could not deposit rewards', async function () {
        await expect(
          stakingRewards
            .connect(sdtWhaleSigner)
            .notifyRewardAmount(parseEther('1'), parseEther('1')),
        ).revertedWith('Wrong caller')
      })
    })

    describe('Claim', async () => {
      beforeEach(async function () {
        await InitializeStakingRewards()
        await sdt.approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](parseEther('1'), 223)
        await sdFRAX3CRVContract
          .connect(deployerSigner)
          .approve(stakingRewards.address, parseEther('10'))
      })

      it('Users with stake deposited could claim a reward if available', async function () {
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('1'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
      })

      it('Users get reward in proportion to the amount they have deposited', async function () {
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('1'),
        )
        ethers.provider.send('evm_increaseTime', [10])
        await stakingRewards.connect(baseOwner).getReward()
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('2'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
      })

      it('Users cannot claim a reward more than once if no rewards are added after the first claim', async function () {
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        ethers.provider.send('evm_increaseTime', [10])
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('3'),
        )
        await expect(stakingRewards.connect(baseOwner).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('3'),
        )
      })

      it('Multiple users could claim their reward', async function () {
        await sdt
          .connect(sdtWhaleSigner)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(sdtWhaleSigner)
          ['stake(uint256,uint256)'](parseEther('1'), 224)
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        ethers.provider.send('evm_increaseTime', [10])
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('3'),
        )
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('3.5'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(sdtWhaleSigner.getAddress()),
        ).to.equal(parseEther('0'))
        await expect(stakingRewards.connect(sdtWhaleSigner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(sdtWhaleSigner.getAddress()),
        ).to.equal(parseEther('0.5'))
      })

      it('Users would be able to claim rewards after each reward deposit', async function () {
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        ethers.provider.send('evm_increaseTime', [10])
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        ethers.provider.send('evm_increaseTime', [10])
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('5.5'),
        )
      })

      it('Users would be able to claim multiple rewards in one go', async function () {
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        ethers.provider.send('evm_increaseTime', [10])

        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        ethers.provider.send('evm_increaseTime', [10])
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('7.5'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
      })

      it('Users cannot claim a reward if they have not staked anything', async function () {
        await expect(
          stakingRewards.connect(sdFrax3CRVWhaleSigner).getReward(),
        ).not.emit(stakingRewards, 'RewardPaid')
      })

      it('we should be able to distribute rewards added by someone else', async function () {
        await sdFRAX3CRVContract
          .connect(sdFrax3CRVWhaleSigner)
          .transfer(stakingRewards.address, parseEther('10'))

        await stakingRewards.notifyRewardAmount(
          parseEther('11'),
          parseEther('1'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('11'))
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('18.5'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
      })

      it('Multiple users could claim their reward with multiple rewards being added', async function () {
        await sdt.approve(stakingRewards.address, parseEther('99'))
        await stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](parseEther('99'), 223)

        await sdt
          .connect(sdtWhaleSigner)
          .approve(stakingRewards.address, parseEther('200'))
        await stakingRewards
          .connect(sdtWhaleSigner)
          ['stake(uint256,uint256)'](parseEther('200'), 224)

        await sdFRAX3CRVContract
          .connect(deployerSigner)
          .approve(stakingRewards.address, parseEther('300'))
        await stakingRewards.notifyRewardAmount(
          parseEther('300'),
          parseEther('300'),
        )

        await sdt
          .connect(userC)
          .approve(stakingRewards.address, parseEther('300'))
        await stakingRewards
          .connect(userC)
          ['stake(uint256,uint256)'](parseEther('300'), 225)

        await sdFRAX3CRVContract
          .connect(deployerSigner)
          .approve(stakingRewards.address, parseEther('300'))
        await stakingRewards.notifyRewardAmount(
          parseEther('300'),
          parseEther('300'),
        )

        ethers.provider.send('evm_increaseTime', [10])

        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        await expect(stakingRewards.connect(sdtWhaleSigner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        await expect(stakingRewards.connect(userC).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('168.5'), //150 claimed
        )

        expect(
          await sdFRAX3CRVContract.balanceOf(sdtWhaleSigner.getAddress()),
        ).to.equal(parseEther('300.5'))
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          parseEther('150'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
      })
    })

    describe('Vesting', async () => {
      beforeEach(async function () {
        await InitializeStakingRewards()
        await sdt.approve(stakingRewards.address, parseEther('1'))
        await sdFRAX3CRVContract
          .connect(deployerSigner)
          .approve(stakingRewards.address, parseEther('10'))
      })

      it('Duration of 7 days & withdrawal after one second of reward notification will result in rewards received for one second', async function () {
        await stakingRewards.setDuration(7 * 86400)
        await stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](parseEther('1'), 223)
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))

        ethers.provider.send('evm_increaseTime', [1])
        await stakingRewards.connect(baseOwner).withdraw(parseEther('1'))
        ethers.provider.send('evm_increaseTime', [24 * 7 * 60 * 60])
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('168.500001653439153439'),
        )

        await expect(stakingRewards.connect(baseOwner).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )

        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0.999998346560846561'))
      })

      it('Staking after reward notification', async function () {
        await stakingRewards.setDuration(7 * 86400)
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        await stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](parseEther('1'), 223)

        ethers.provider.send('evm_increaseTime', [24 * 7 * 60 * 60])
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('169.499999999999907200'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0.000001653439246239'))
      })

      it('Staking before reward notification: Duration 7 days', async function () {
        await stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](parseEther('1'), 223)
        await stakingRewards.setDuration(7 * 86400)
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))

        ethers.provider.send('evm_increaseTime', [24 * 7 * 60 * 60])
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('170.499999999999814400'), //Increment of 0.999999999999907200
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0.000000000000092800')) //There is a loss of some amount
      })

      it('Staking before reward notification: Duration 10 days', async function () {
        await stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](parseEther('1'), 223)
        await stakingRewards.setDuration(10 * 86400)
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))

        ethers.provider.send('evm_increaseTime', [24 * 10 * 60 * 60])
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('171.499999999999462400'), //Increment of 0.999999999999648000
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0.000000000000352000')) //There is a loss of some amount
      })

      it('Staking midway during the vesting period: Duration 7 days', async function () {
        await stakingRewards.setDuration(7 * 86400)
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        ethers.provider.send('evm_increaseTime', [24 * 3.5 * 60 * 60])
        await stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](parseEther('1'), 223)
        ethers.provider.send('evm_increaseTime', [24 * 3.5 * 60 * 60])
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('171.999999999999416000'), //Increment of 0.499,999,999,999,953,600
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0.500000000000046400')) //There is a loss of some amount 92800
      })

      it('Staking after duration expires', async function () {
        const initBalance = parseEther('171.999999999999416000')
        //Notify reward
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          initBalance,
        )
        ethers.provider.send('evm_increaseTime', [10])

        //Stake after expiration
        await stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](parseEther('1'), 223)

        //Claim reward
        await expect(stakingRewards.connect(baseOwner).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )

        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          initBalance, //Balance do not change as the staking was done after the notification of rewards
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
      })

      it('1.1.1 Stake before notification & withdrawal during vesting period', async function () {
        //Stake
        await stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](parseEther('1'), 223)

        //10 sec passes & rewards are notified
        ethers.provider.send('evm_increaseTime', [10])
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        //User claims the rewards
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('172.999999999999416000'), // Gets 1 reward token
        )
        ethers.provider.send('evm_increaseTime', [10])

        //Users withdraw their stake
        await stakingRewards.connect(baseOwner).withdraw(parseEther('1'))

        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('172.999999999999416000'),
        )
      })

      it('1.1.2 Stake before notification & withdrawal during vesting period', async function () {
        //Stake
        await stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](parseEther('1'), 223)

        //10 sec passes & rewards are notified
        ethers.provider.send('evm_increaseTime', [10])
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        ethers.provider.send('evm_increaseTime', [1])
        //User claims the rewards
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )

        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('173.999999999999416000'), // Gets 1 reward token
        )

        //Users withdraw their stake
        await stakingRewards.connect(baseOwner).withdraw(parseEther('1'))

        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('173.999999999999416000'),
        )
      })

      it('1.1.3 Stake before notification & withdrawal during vesting period', async function () {
        //Stake
        await stakingRewards
          .connect(baseOwner)
          ['stake(uint256,uint256)'](parseEther('1'), 223)

        //10 sec passes & rewards are notified
        ethers.provider.send('evm_increaseTime', [10])
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        ethers.provider.send('evm_increaseTime', [1])

        //Users withdraw their stake
        await stakingRewards.connect(baseOwner).withdraw(parseEther('1'))
        //User claims the rewards
        await expect(stakingRewards.connect(baseOwner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )

        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
        expect(await sdFRAX3CRVContract.balanceOf(baseOwner.address)).to.equal(
          parseEther('174.999999999999416000'), // Gets 1 reward token
        )
      })

      it('1.2.1 Stake before notification & withdrawal during vesting period', async function () {
        //Stake
        await sdt
          .connect(sdtWhaleSigner)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(sdtWhaleSigner)
          ['stake(uint256,uint256)'](parseEther('1'), 224)

        //10 sec passes & rewards are notified
        ethers.provider.send('evm_increaseTime', [10])
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        //User claims the rewards
        await expect(stakingRewards.connect(sdtWhaleSigner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
        expect(
          await sdFRAX3CRVContract.balanceOf(sdtWhaleSigner.getAddress()),
        ).to.equal(
          parseEther('301.5'), // Gets 1 reward token
        )

        //Users withdraw their stake
        await stakingRewards.connect(sdtWhaleSigner).withdraw(parseEther('1'))

        ethers.provider.send('evm_increaseTime', [1])

        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
        expect(
          await sdFRAX3CRVContract.balanceOf(sdtWhaleSigner.getAddress()),
        ).to.equal(parseEther('301.5'))
      })

      it('1.2.2 Stake before notification & withdrawal during vesting period', async function () {
        //Stake
        await sdt
          .connect(sdtWhaleSigner)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(sdtWhaleSigner)
          ['stake(uint256,uint256)'](parseEther('1'), 224)

        //10 sec passes & rewards are notified
        ethers.provider.send('evm_increaseTime', [10])
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        //Users withdraw their stake
        await stakingRewards.connect(sdtWhaleSigner).withdraw(parseEther('1'))

        //User claims the rewards
        await expect(stakingRewards.connect(sdtWhaleSigner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
        expect(
          await sdFRAX3CRVContract.balanceOf(sdtWhaleSigner.getAddress()),
        ).to.equal(
          parseEther('302.5'), // Gets 1 reward token
        )
      })

      it('1.2.3 Stake before notification & withdrawal during vesting period', async function () {
        //Stake
        await sdt
          .connect(sdtWhaleSigner)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(sdtWhaleSigner)
          ['stake(uint256,uint256)'](parseEther('1'), 224)

        //10 sec passes & rewards are notified
        ethers.provider.send('evm_increaseTime', [10])
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        //Users withdraw their stake
        await stakingRewards.connect(sdtWhaleSigner).withdraw(parseEther('1'))

        ethers.provider.send('evm_increaseTime', [1])

        //User claims the rewards
        await expect(stakingRewards.connect(sdtWhaleSigner).getReward()).emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('0'))
        expect(
          await sdFRAX3CRVContract.balanceOf(sdtWhaleSigner.getAddress()),
        ).to.equal(
          parseEther('303.5'), // Gets 1 reward token
        )
      })

      it('1.3.1 No reward as withdraw before notification', async function () {
        const userRewarTokenBalance = parseEther('150')
        //Stake
        await sdt
          .connect(userC)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(userC)
          ['stake(uint256,uint256)'](parseEther('1'), 225)
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance,
        )
        //Users withdraw their stake
        await stakingRewards.connect(userC).withdraw(parseEther('1'))

        //10 sec passes & rewards are notified
        ethers.provider.send('evm_increaseTime', [10])
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        //User claims the rewards
        await expect(stakingRewards.connect(userC).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance, //No rewards received
        )
      })

      it('1.3.2 No reward as withdraw before notification', async function () {
        const userRewarTokenBalance = parseEther('150')
        //Stake
        await sdt
          .connect(userC)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(userC)
          ['stake(uint256,uint256)'](parseEther('1'), 225)
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance,
        )
        //Users withdraw their stake
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('19'))
        await stakingRewards.connect(userC).withdraw(parseEther('1'))
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('20'))
        //10 sec passes & rewards are notified
        ethers.provider.send('evm_increaseTime', [10])
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        ethers.provider.send('evm_increaseTime', [1])

        //User claims the rewards
        await expect(stakingRewards.connect(userC).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance, //No rewards received
        )
      })

      it('2.1.1 Staking during duration & claim during duration', async function () {
        const userRewarTokenBalance = parseEther('150')
        //Notify
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        //Stake
        await sdt
          .connect(userC)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(userC)
          ['stake(uint256,uint256)'](parseEther('1'), 225)
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance,
        )

        //User claims the rewards
        await expect(stakingRewards.connect(userC).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance, //No rewards received
        )

        ethers.provider.send('evm_increaseTime', [1])
        //Users withdraw their stake
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('19'))
        await stakingRewards.connect(userC).withdraw(parseEther('1'))
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('20'))
      })

      it('2.1.2 Staking during duration & claim after expiry', async function () {
        const userRewarTokenBalance = parseEther('150')
        //Notify
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        //Stake
        await sdt
          .connect(userC)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(userC)
          ['stake(uint256,uint256)'](parseEther('1'), 225)
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance,
        )

        ethers.provider.send('evm_increaseTime', [1])
        //User claims the rewards
        await expect(stakingRewards.connect(userC).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance, //No rewards received
        )

        //Users withdraw their stake
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('19'))
        await stakingRewards.connect(userC).withdraw(parseEther('1'))
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('20'))
      })

      it('2.1.3 Staking during duration & claim after expiry & withdrawal', async function () {
        const userRewarTokenBalance = parseEther('150')
        //Notify
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        //Stake
        await sdt
          .connect(userC)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(userC)
          ['stake(uint256,uint256)'](parseEther('1'), 225)
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance,
        )

        ethers.provider.send('evm_increaseTime', [1])
        //Users withdraw their stake
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('19'))
        await stakingRewards.connect(userC).withdraw(parseEther('1'))
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('20'))

        //User claims the rewards
        await expect(stakingRewards.connect(userC).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance, //No rewards received
        )
      })

      it('2.2.1 Staking,claim withdraw during duration', async function () {
        const userRewarTokenBalance = parseEther('150')
        //Notify
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        //Stake
        await sdt
          .connect(userC)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(userC)
          ['stake(uint256,uint256)'](parseEther('1'), 225)
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance,
        )

        //User claims the rewards
        await expect(stakingRewards.connect(userC).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance, //No rewards received
        )
        //Users withdraw their stake
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('19'))
        await stakingRewards.connect(userC).withdraw(parseEther('1'))
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('20'))
      })

      it('2.2.2 Staking, withdraw, claim during duration', async function () {
        const userRewarTokenBalance = parseEther('150')
        //Notify
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        //Stake
        await sdt
          .connect(userC)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(userC)
          ['stake(uint256,uint256)'](parseEther('1'), 225)
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance,
        )

        //Users withdraw their stake
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('19'))
        await stakingRewards.connect(userC).withdraw(parseEther('1'))
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('20'))

        //User claims the rewards
        await expect(stakingRewards.connect(userC).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance, //No rewards received
        )
      })

      it('2.2.3 Staking, withdraw during duration & claim after expiry', async function () {
        const userRewarTokenBalance = parseEther('150')
        //Notify
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )

        //Stake
        await sdt
          .connect(userC)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(userC)
          ['stake(uint256,uint256)'](parseEther('1'), 225)
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance,
        )

        //Users withdraw their stake
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('19'))
        await stakingRewards.connect(userC).withdraw(parseEther('1'))
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('20'))

        ethers.provider.send('evm_increaseTime', [1])

        //User claims the rewards
        await expect(stakingRewards.connect(userC).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance, //No rewards received
        )
      })

      it('2.3.1 Stake after expiry', async function () {
        const userRewarTokenBalance = parseEther('150')
        //Notify
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        ethers.provider.send('evm_increaseTime', [1])
        //Stake
        await sdt
          .connect(userC)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(userC)
          ['stake(uint256,uint256)'](parseEther('1'), 225)
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance,
        )

        //User claims the rewards
        await expect(stakingRewards.connect(userC).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance, //No rewards received
        )

        //Users withdraw their stake
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('19'))
        await stakingRewards.connect(userC).withdraw(parseEther('1'))
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('20'))
      })

      it('2.3.2 Stake after expiry, claim after withdraw', async function () {
        const userRewarTokenBalance = parseEther('150')
        //Notify
        await stakingRewards.notifyRewardAmount(
          parseEther('1'),
          parseEther('1'),
        )
        ethers.provider.send('evm_increaseTime', [1])
        //Stake
        await sdt
          .connect(userC)
          .approve(stakingRewards.address, parseEther('1'))
        await stakingRewards
          .connect(userC)
          ['stake(uint256,uint256)'](parseEther('1'), 225)
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance,
        )

        //Users withdraw their stake
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('19'))
        await stakingRewards.connect(userC).withdraw(parseEther('1'))
        expect(await sdt.balanceOf(userC.getAddress())).equal(parseEther('20'))

        //User claims the rewards
        await expect(stakingRewards.connect(userC).getReward()).not.emit(
          stakingRewards,
          'RewardPaid',
        )
        expect(
          await sdFRAX3CRVContract.balanceOf(stakingRewards.address),
        ).to.equal(parseEther('1'))
        expect(await sdFRAX3CRVContract.balanceOf(userC.getAddress())).to.equal(
          userRewarTokenBalance, //No rewards received
        )
      })
    })
  })
})
