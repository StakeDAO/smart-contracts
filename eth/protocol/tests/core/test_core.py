import pytest
from brownie import *


@pytest.fixture(scope="module", autouse=True)
def deployedContracts():

    # list of 10 use-n-throw addresses
    addresses = ['0x4ce799e6eD8D64536b67dD428565d52A531B3640', '0x4e14672D1Ed1FEFAc9948456006a4015D186C15E', '0x6EDfA9fb275f389a641c8C3c85DdF29dF2Ca8EC7', '0x57813f12d90177bE50ec25Fb60bd2BaC1558fd9C', '0xF65fA4C233CDA7aA7a3563d824809231b138cf11',
                 '0x10Cdd8CDaa3c402AA2fc3d6a29b6D79424f77fDB', '0x8E60704Fa16bE888a0EcBFD68DF34DfC9D066A15', '0x6FE46dd39f8289218f99448DEdAFa2fD4C483aDc', '0x0D935F1Da128b34698Dc3274a9F39bAF2D6C79eE', '0x02a22054d42C50797dcBFeE3077C767b2c9864EB']

    # account used for executing transactions
    DEFAULT_DEPLOYER_ACCOUNT = accounts.at(addresses[0], force=True)

    # Existing GnosisSafe mainnet address
    GNOSISSAFE_MASTERCOPY = '0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F'

    # Existing GnosisSafeProxyFactory mainnet address
    GNOSISSAFE_PROXY_FACTORY = '0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B'

    # Curve TokenMinter mainnet address
    TOKEN_MINTER = '0xd061D61a4d941c39E5453435B6345Dc261C2fcE0'

    # YEARN_DEPLOYER = accounts.at(addresses[1], force=True)

    # an array of 3 owners of governance multisig
    GOVERNANCE_OWNERS = []
    for i in range(2, 5):
        GOVERNANCE_OWNERS.append(accounts.at(addresses[i], force=True))

    # Strategist account
    STRATEGIST = accounts.at(addresses[5], force=True)

    # trx data for setting up owners and threshold for governance multisig
    DATA = "0xb63e800d0000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030000000000000000000000004e14672d1ed1fefac9948456006a4015d186c15e0000000000000000000000006edfa9fb275f389a641c8c3c85ddf29df2ca8ec700000000000000000000000057813f12d90177be50ec25fb60bd2bac1558fd9c00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000"

    # DAI mainnet token address
    DAI = '0x6B175474E89094C44Da98b954EedeAC495271d0F'

    # sbtcCrv Token mainnet address
    SBTC_CRV = '0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3'

    # 3Crv Token mainnet address
    THREE_CRV = '0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490'

    # eursCrv Token mainnet address
    EURS_CRV = '0x194eBd173F6cDacE046C53eACcE9B953F28411d1'

    # Keepr address
    Keep3r = '0x1cEB5cB57C4D4E2b2433641b95Dd330A33185A44'

    # CurveYCRVVoter mainnet address
    # CurveYCRVVoter = '0xF147b8125d2ef93FB6965Db97D6746952a133934'

    # StrategyProxy mainnet address
    # StrategyProxyAddress = '0x7A1848e7847F3f5FfB4d8e63BdB9569db535A4f0'

    # 3Crv minter
    THREE_CRV_MINTER = '0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7'

    # sbtc minter
    SBTC_CRV_MINTER = '0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714'

    # eursCrv minter
    EURS_CRV_MINTER = '0x0Ce6a5fF5217e38315f87032CF90686C96627CAA'

    # DAI bags
    DAI_HOLDER = '0x70178102AA04C5f0E54315aA958601eC9B7a4E08'

    # number of SDT minted per block at the time of deployment
    SDT_PER_BLOCK = 1000

    sender = {'from': DEFAULT_DEPLOYER_ACCOUNT}

    CRV_HOLDER = '0x4ce799e6eD8D64536b67dD428565d52A531B3640'

    crv = CRV.at('0xD533a949740bb3306d119CC777fa900bA034cd52')

    crvBal = crv.balanceOf(CRV_HOLDER)

    crv.transfer(DEFAULT_DEPLOYER_ACCOUNT, crvBal, {'from': CRV_HOLDER})

    dai = VaultToken.at(DAI)

    daiBal = dai.balanceOf(DAI_HOLDER)

    dai.transfer(DEFAULT_DEPLOYER_ACCOUNT, daiBal, {'from': DAI_HOLDER})

    # Deploy GnosisSafeProxyFactory
    governanceProxyFactory = GnosisSafeProxyFactory.at(
        GNOSISSAFE_PROXY_FACTORY)

    # Deploy GnosisSafeProxy (Governance) and setup owners, threashold
    governanceGSPTx = governanceProxyFactory.createProxyWithNonce(
        GNOSISSAFE_MASTERCOPY, DATA, 0, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    governanceGSPAddress = governanceGSPTx.new_contracts[0]

    # Deploy SDT
    sdtToken = SDT.deploy({'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Mint SDT
    sdtSupply = 1000000000000000000000
    sdtToken.mint(DEFAULT_DEPLOYER_ACCOUNT, sdtSupply, sender)

    # Deploy TimelockGovernance
    timelockGovernance = Timelock.deploy(
        governanceGSPAddress, 28800, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy MasterChef
    masterchef = MasterChef.deploy(
        sdtToken, governanceGSPAddress, SDT_PER_BLOCK, web3.eth.blockNumber, 0, sender)

    # Transferring the MasterChef contract ownership to the TimelockGovernance
    # masterchef.transferOwnership(timelockGovernance.address, sender)

    # Transferring the SDT contract ownership to the MasterChef
    sdtToken.transferOwnership(masterchef.address, sender)

    # Deploy GovernanceStaking
    governanceStaking = StakeDaoGovernance.deploy(
        {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Initialize Governance Staking
    governanceStaking.initialize(0, governanceGSPAddress, DAI, sdtToken.address, {
                                 'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy TreasuryZap
    treasuryZap = TreasuryZap.deploy({'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy TreasuryVault
    treasuryVault = TreasuryVault.deploy(governanceStaking.address, DAI, treasuryZap.address, {
                                         'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy CurveYCRVVoter
    curveYCRVVoter = CurveYCRVVoter.deploy({'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Whitelist CurveYCRVVoter
    smartWalletWhitelist = Contract(
        '0xca719728Ef172d0961768581fdF35CB116e0B7a4')
    smartWalletWhitelist.approveWallet(
        curveYCRVVoter.address, {'from': '0x40907540d8a6C65c637785e8f8B742ae6b0b9968'})

    # Fund CurveYCRVVoter to create a lock
    crv.transfer(curveYCRVVoter.address, 1, sender)

    # Update crvBal
    crvBal = crv.balanceOf(CRV_HOLDER)

    # Create a lock in Curve Voting Escrow
    curveYCRVVoter.createLock(
        1, chain.time()+126144000, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy StrategyProxy
    strategyProxy = StrategyProxy.deploy({'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Set CurveYCRVVoter strategy to StrategyProxy
    curveYCRVVoter.setStrategy(strategyProxy.address, {
                               'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer CurveYCRVVoter governance to Governance (GSP)
    curveYCRVVoter.setGovernance(governanceGSPAddress, {
                                 'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy veCurveVault
    veCurve = veCurveVault.deploy({'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy Controller
    controller = Controller.deploy(treasuryVault.address, {
                                   'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy CrvStrategyKeep3r
    crvStrategyKeep3r = CrvStrategyKeep3r.deploy(
        DEFAULT_DEPLOYER_ACCOUNT, sender)

    # setKeep3r
    crvStrategyKeep3r.setKeep3r(Keep3r, sender)

    # Deploy eursCrv Vault
    eursCrvVault = yVault.deploy(EURS_CRV, controller.address, {
        'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer eursCrv Vault governance to Governance (GSP)
    eursCrvVault.setGovernance(governanceGSPAddress, {
        'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy strategyCurveEursCrvVoterProxy
    strategyCurveEursCrvVoterProxy = StrategyCurveEursCrvVoterProxy.deploy(
        controller.address, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Register strategyCurveEursCrvVoterProxy in StrategyProxy
    strategyProxy.approveStrategy(strategyCurveEursCrvVoterProxy.address, {
        'from': DEFAULT_DEPLOYER_ACCOUNT})

    # set proxy to StrategyProxy
    strategyCurveEursCrvVoterProxy.setProxy(
        strategyProxy.address, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer strategyCurveEursCrvVoterProxy strategist role to CrvStrategyKeep3r
    strategyCurveEursCrvVoterProxy.setStrategist(
        STRATEGIST, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer strategyCurveEursCrvVoterProxy governance to Governance (GSP)
    strategyCurveEursCrvVoterProxy.setGovernance(
        governanceGSPAddress, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Approve the strategyCurveEursCrvVoterProxy strategy in Controller
    controller.approveStrategy(EURS_CRV, strategyCurveEursCrvVoterProxy.address, {
        'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Register strategyCurveEursCrvVoterProxy in Controller
    controller.setStrategy(EURS_CRV, strategyCurveEursCrvVoterProxy.address, {
        'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Register eursCrv Vault in Controller
    controller.setVault(EURS_CRV, eursCrvVault.address, {
                        'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy 3pool Vault
    threePoolVault = yVault.deploy(THREE_CRV, controller.address, {
                                   'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer 3pool Vault governance to Governance (GSP)
    threePoolVault.setGovernance(governanceGSPAddress, {
                                 'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy StrategyCurve3CrvVoterProxy
    strategyCurve3CrvVoterProxy = StrategyCurve3CrvVoterProxy.deploy(
        controller.address, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Register strategyCurve3CrvVoterProxy in StrategyProxy
    strategyProxy.approveStrategy(strategyCurve3CrvVoterProxy.address, {
                                  'from': DEFAULT_DEPLOYER_ACCOUNT})

    # set proxy to StrategyProxy
    strategyCurve3CrvVoterProxy.setProxy(
        strategyProxy.address, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer StrategyCurve3CrvVoterProxy strategist role to CrvStrategyKeep3r
    strategyCurve3CrvVoterProxy.setStrategist(
        STRATEGIST, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer StrategyCurve3CrvVoterProxy governance to Governance (GSP)
    strategyCurve3CrvVoterProxy.setGovernance(
        governanceGSPAddress, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Approve the StrategyCurve3CrvVoterProxy strategy in Controller
    controller.approveStrategy(THREE_CRV, strategyCurve3CrvVoterProxy.address, {
                               'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Register StrategyCurve3CrvVoterProxy in Controller
    controller.setStrategy(THREE_CRV, strategyCurve3CrvVoterProxy.address, {
                           'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Register 3pool Vault in Controller
    controller.setVault(THREE_CRV, threePoolVault.address,
                        {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy sbtc Vault
    sbtcVault = yVault.deploy(SBTC_CRV, controller.address, {
                              'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer sbtc Vault governance to Governance (GSP)
    sbtcVault.setGovernance(governanceGSPAddress, {
                            'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Deploy StrategyCurveBTCVoterProxy
    strategyCurveBTCVoterProxy = StrategyCurveBTCVoterProxy.deploy(
        controller.address, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Register strategyCurveBTCVoterProxy in StrategyProxy
    strategyProxy.approveStrategy(strategyCurveBTCVoterProxy.address, {
                                  'from': DEFAULT_DEPLOYER_ACCOUNT})

    # set proxy to StrategyProxy
    strategyCurveBTCVoterProxy.setProxy(
        strategyProxy.address, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer StrategyCurveBTCVoterProxy strategist role to CrvStrategyKeep3r
    strategyCurveBTCVoterProxy.setStrategist(
        STRATEGIST, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer StrategyCurveBTCVoterProxy governance to Governance (GSP)
    strategyCurveBTCVoterProxy.setGovernance(
        governanceGSPAddress, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Approve the StrategyCurveBTCVoterProxy strategy in Controller
    controller.approveStrategy(SBTC_CRV, strategyCurveBTCVoterProxy.address, {
                               'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Register StrategyCurveBTCVoterProxy in Controller
    controller.setStrategy(SBTC_CRV, strategyCurveBTCVoterProxy.address, {
                           'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Register sbtc Vault in Controller
    controller.setVault(SBTC_CRV, sbtcVault.address, {
                        'from': DEFAULT_DEPLOYER_ACCOUNT})

    # set Strategist for Controller
    controller.setStrategist(STRATEGIST, {'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer Controller governance to Governance (GSP)
    # TODO: This transfer of governance should be ususally done just after
    #       the creation of the Controller. But we delay the governance
    #       transfer for simplicity.
    controller.setGovernance(governanceGSPAddress, {
                             'from': DEFAULT_DEPLOYER_ACCOUNT})

    # Transfer StrategyProxy governance to Governance (GSP)
    strategyProxy.setGovernance(governanceGSPAddress, {
                                'from': DEFAULT_DEPLOYER_ACCOUNT})

    bal = threePoolVault.balance()

    sbtc = VaultToken.at(SBTC_CRV)
    threeCrv = VaultToken.at(THREE_CRV)
    eursCrv = VaultToken.at(EURS_CRV)

    sbtcBal = 10000000000000000000000000000
    threeCrvBal = 10000000000000000000000000000
    eursCrvBal = 10000000000000000000000000000

    threeCrv.mint(DEFAULT_DEPLOYER_ACCOUNT, threeCrvBal,
                  {'from': THREE_CRV_MINTER})
    eursCrv.mint(DEFAULT_DEPLOYER_ACCOUNT, eursCrvBal,
                 {'from': EURS_CRV_MINTER})
    sbtc.mint(DEFAULT_DEPLOYER_ACCOUNT, sbtcBal, {'from': SBTC_CRV_MINTER})

    threeCrv.approve(threePoolVault.address, threeCrvBal, sender)
    eursCrv.approve(eursCrvVault.address, eursCrvBal, sender)
    sbtc.approve(sbtcVault.address, sbtcBal, sender)

    return {'threePoolVault': threePoolVault, 'eursCrvVault': eursCrvVault, 'sbtcVault': sbtcVault, 'sender': sender, 'DEFAULT_DEPLOYER_ACCOUNT': DEFAULT_DEPLOYER_ACCOUNT, 'eursCrv': eursCrv, 'threeCrv': threeCrv, 'sbtc': sbtc, 'strategyCurveEursCrvVoterProxy': strategyCurveEursCrvVoterProxy, 'strategyCurve3CrvVoterProxy': strategyCurve3CrvVoterProxy, 'strategyCurveBTCVoterProxy': strategyCurveBTCVoterProxy, 'veCurve': veCurve, 'crv': crv, 'crvBal': crvBal, 'threeCrvBal': threeCrvBal, 'eursCrvBal': eursCrvBal, 'sbtcBal': sbtcBal, 'veCurve': veCurve, 'STRATEGIST': STRATEGIST, 'controller': controller, 'governanceGSPAddress': governanceGSPAddress, 'daiBal': daiBal, 'dai': dai, 'sdtToken': sdtToken, 'masterchef': masterchef, 'timelockGovernance': timelockGovernance, 'treasuryVault': treasuryVault, 'governanceStaking': governanceStaking}


""" @pytest.fixture(autouse=True)
def isolation(fn_isolation):
    print("isolation fixture")
    pass """

################################## Treasury tests #####################################


def test_Treasury_swapViaZap(deployedContracts):
    treasuryVault = deployedContracts['treasuryVault']
    sbtc = deployedContracts['sbtc']
    dai = deployedContracts['dai']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    treasuryVault.setAuthorized(DEFAULT_DEPLOYER_ACCOUNT, sender)

    sbtc.transfer(treasuryVault.address, 200000000000000000, sender)

    beforeSbtcBal = sbtc.balanceOf(treasuryVault.address)
    beforeDaiBal = dai.balanceOf(treasuryVault.address)

    tx = treasuryVault.swapViaZap(
        sbtc.address, dai.address, 100000000000000000, sender)

    amountOut = tx.return_value

    afterSbtcBal = sbtc.balanceOf(treasuryVault.address)
    afterDaiBal = dai.balanceOf(treasuryVault.address)

    print("Amount Out", amountOut)

    assert afterSbtcBal == beforeSbtcBal - 100000000000000000
    assert afterDaiBal == beforeDaiBal + amountOut


def test_Treasury_toGovernance(deployedContracts):
    treasuryVault = deployedContracts['treasuryVault']
    sbtc = deployedContracts['sbtc']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    beforeGovBal = sbtc.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeTreasuryBal = sbtc.balanceOf(treasuryVault.address)

    treasuryVault.toGovernance(sbtc.address, beforeTreasuryBal, sender)

    afterGovBal = sbtc.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterTreasuryBal = sbtc.balanceOf(treasuryVault.address)

    assert afterGovBal == beforeGovBal + beforeTreasuryBal
    assert afterTreasuryBal == 0


def test_Treasury_toGovernanceStaking(deployedContracts):
    treasuryVault = deployedContracts['treasuryVault']
    dai = deployedContracts['dai']
    sender = deployedContracts['sender']
    governanceStaking = deployedContracts['governanceStaking']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    beforeTreasuryBal = dai.balanceOf(treasuryVault.address)
    beforeGovStakingBal = dai.balanceOf(governanceStaking)

    governanceStaking.setRewardDistribution(treasuryVault.address, sender)

    treasuryVault.toGovernanceStaking(sender)

    afterTreasuryBal = dai.balanceOf(treasuryVault.address)
    afterGovStakingBal = dai.balanceOf(governanceStaking)

    afterGovStakingBal == beforeGovStakingBal + beforeTreasuryBal
    afterTreasuryBal == 0


################################## Governance DAO tests #####################################
# TODO: add Governance DAO tests

def test_governance_voter_register(deployedContracts):
    governanceStaking = deployedContracts['governanceStaking']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    governanceStaking.register(sender)

    assert governanceStaking.voters(DEFAULT_DEPLOYER_ACCOUNT) == True


def test_governance_voter_revoke(deployedContracts):
    governanceStaking = deployedContracts['governanceStaking']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    governanceStaking.revoke(sender)

    assert governanceStaking.voters(DEFAULT_DEPLOYER_ACCOUNT) == False


def test_governance_stake(deployedContracts):
    governanceStaking = deployedContracts['governanceStaking']
    sender = deployedContracts['sender']
    sdtToken = deployedContracts['sdtToken']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    sdtSupply = sdtToken.totalSupply()

    governanceStaking.register(sender)

    sdtToken.approve(governanceStaking.address, sdtSupply, sender)

    assert sdtToken.allowance(DEFAULT_DEPLOYER_ACCOUNT,
                              governanceStaking.address) == sdtSupply

    governanceStaking.stake(sdtSupply, sender)

    assert governanceStaking.votes(DEFAULT_DEPLOYER_ACCOUNT) == sdtSupply
    assert governanceStaking.balanceOf(DEFAULT_DEPLOYER_ACCOUNT) == sdtSupply


def test_governance_proposal(deployedContracts):
    governanceStaking = deployedContracts['governanceStaking']
    sender = deployedContracts['sender']
    daiBal = deployedContracts['daiBal']
    dai = deployedContracts['dai']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    EXECUTOR = accounts[9].address

    governanceStaking.setRewardDistribution(DEFAULT_DEPLOYER_ACCOUNT, sender)

    dai.approve(governanceStaking.address, daiBal, sender)
    governanceStaking.notifyRewardAmount(daiBal, sender)

    governanceStaking.propose(EXECUTOR, "link to proposal", sender)

    proposal = governanceStaking.proposals(0)

    assert proposal[0] == 0
    assert proposal[1] == DEFAULT_DEPLOYER_ACCOUNT
    assert proposal[2] == 0
    assert proposal[3] == 0
    assert proposal[4] == web3.eth.blockNumber
    assert proposal[5] == governanceStaking.period() + web3.eth.blockNumber
    assert proposal[6] == EXECUTOR
    assert proposal[7] == "link to proposal"
    assert proposal[8] == governanceStaking.votes(DEFAULT_DEPLOYER_ACCOUNT)
    assert proposal[9] == 0
    assert proposal[10] == governanceStaking.quorum()
    assert proposal[11] == True


def test_governance_getReward(deployedContracts):

    governanceStaking = deployedContracts['governanceStaking']
    sender = deployedContracts['sender']
    daiBal = deployedContracts['daiBal']
    dai = deployedContracts['dai']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    assert governanceStaking.rewardPerToken() > 0
    assert governanceStaking.earned(DEFAULT_DEPLOYER_ACCOUNT) > 0
    assert dai.balanceOf(DEFAULT_DEPLOYER_ACCOUNT) == 0

    governanceStaking.getReward(sender)

    assert dai.balanceOf(DEFAULT_DEPLOYER_ACCOUNT) > 0

    governanceStakingBal = dai.balanceOf(governanceStaking.address)
    senderBal = dai.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)

    # assert daiBal == governanceStakingBal + senderBal


def test_governance_voteFor(deployedContracts):
    governanceStaking = deployedContracts['governanceStaking']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    votes = governanceStaking.votes(DEFAULT_DEPLOYER_ACCOUNT)

    beforeFor = governanceStaking.proposals(0)[2]

    governanceStaking.voteFor(0, sender)

    afterFor = governanceStaking.proposals(0)[2]

    assert afterFor == beforeFor + votes


def test_governance_voteAgainst(deployedContracts):
    governanceStaking = deployedContracts['governanceStaking']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    votes = governanceStaking.votes(DEFAULT_DEPLOYER_ACCOUNT)

    beforeAgainst = governanceStaking.proposals(0)[3]

    governanceStaking.voteAgainst(0, sender)

    afterAgainst = governanceStaking.proposals(0)[3]

    assert afterAgainst == beforeAgainst + votes


def test_governance_withdraw(deployedContracts):
    governanceStaking = deployedContracts['governanceStaking']
    sender = deployedContracts['sender']
    sdtToken = deployedContracts['sdtToken']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    totalSupply = sdtToken.totalSupply()

    chain.mine(governanceStaking.voteLock(
        DEFAULT_DEPLOYER_ACCOUNT) - web3.eth.blockNumber + 1)

    beforeBal = sdtToken.balanceOf(governanceStaking.address)

    governanceStaking.withdraw(beforeBal, sender)

    afterBal = sdtToken.balanceOf(governanceStaking.address)

    assert totalSupply == beforeBal + afterBal


def test_governance_seize(deployedContracts):
    governanceStaking = deployedContracts['governanceStaking']
    sender = deployedContracts['sender']
    sdtToken = deployedContracts['sdtToken']
    threeCrv = deployedContracts['threeCrv']
    governanceGSPAddress = deployedContracts['governanceGSPAddress']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    threeCrv.transfer(governanceStaking.address, 100, sender)

    gspBalBefore = threeCrv.balanceOf(governanceGSPAddress)
    govStakingBalBefore = threeCrv.balanceOf(governanceStaking)

    governanceStaking.seize(threeCrv, 100, {'from': governanceGSPAddress})

    gspBalAfter = threeCrv.balanceOf(governanceGSPAddress)
    govStakingBalAfter = threeCrv.balanceOf(governanceStaking)

    assert gspBalAfter == gspBalBefore + 100
    assert govStakingBalAfter == govStakingBalBefore - 100


################################## MasterChef tests #####################################


def test_MasterChef_add(deployedContracts):
    masterchef = deployedContracts['masterchef']
    threePoolVault = deployedContracts['threePoolVault']
    sender = deployedContracts['sender']

    masterchef.add(100, threePoolVault, False, sender)

    poolInfo = masterchef.poolInfo(0)

    assert poolInfo[0] == threePoolVault.address
    assert poolInfo[1] == 100
    assert poolInfo[2] == web3.eth.blockNumber
    assert poolInfo[3] == 0


def test_MasterChef_set(deployedContracts):
    masterchef = deployedContracts['masterchef']
    threePoolVault = deployedContracts['threePoolVault']
    sender = deployedContracts['sender']

    masterchef.set(0, 1000, False, sender)

    poolInfo = masterchef.poolInfo(0)

    assert poolInfo[0] == threePoolVault.address
    assert poolInfo[1] == 1000
    assert poolInfo[2] == web3.eth.blockNumber - 1
    assert poolInfo[3] == 0


def test_MasterChef_setSdtPerBlock(deployedContracts):
    masterchef = deployedContracts['masterchef']
    sender = deployedContracts['sender']

    masterchef.setSdtPerBlock(2000, sender)

    assert masterchef.sdtPerBlock() == 2000


def test_MasterChef_setBonusEndBlock(deployedContracts):
    masterchef = deployedContracts['masterchef']
    sender = deployedContracts['sender']

    blockNum = web3.eth.blockNumber + 1000

    masterchef.setBonusEndBlock(blockNum)

    assert masterchef.bonusEndBlock() == blockNum


def test_MasterChef_setDevFundDivRate(deployedContracts):
    masterchef = deployedContracts['masterchef']
    threePoolVault = deployedContracts['threePoolVault']
    sender = deployedContracts['sender']

    masterchef.setDevFundDivRate(60)

    assert masterchef.devFundDivRate() == 60


def test_MasterChef_deposit(deployedContracts):
    masterchef = deployedContracts['masterchef']
    threePoolVault = deployedContracts['threePoolVault']
    threeCrv = deployedContracts['threeCrv']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    senderBal = threeCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)

    threePoolVault.deposit(1000, sender)

    threePoolVault.approve(masterchef.address, 1000, sender)

    masterchefBalBefore = threePoolVault.balanceOf(masterchef.address)
    senderBalBefore = threePoolVault.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)

    masterchef.deposit(0, 1000, sender)

    masterchefBalAfter = threePoolVault.balanceOf(masterchef.address)
    senderBalAfter = threePoolVault.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)

    assert masterchefBalAfter == masterchefBalBefore + 1000
    assert senderBalAfter == senderBalBefore - 1000


def test_MasterChef_updatePool(deployedContracts):
    masterchef = deployedContracts['masterchef']
    threePoolVault = deployedContracts['threePoolVault']
    sender = deployedContracts['sender']
    sdtToken = deployedContracts['sdtToken']

    assert sdtToken.totalSupply() == 1000000000000000000000
    assert masterchef.poolInfo(0)[3] == 0

    masterchef.updatePool(0, sender)

    assert sdtToken.totalSupply() > 1000000000000000000000
    assert masterchef.poolInfo(0)[3] > 0


def test_MasterChef_withdraw(deployedContracts):
    masterchef = deployedContracts['masterchef']
    threePoolVault = deployedContracts['threePoolVault']
    sender = deployedContracts['sender']
    sdtToken = deployedContracts['sdtToken']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']

    chain.mine(1)

    masterchefBalBefore = threePoolVault.balanceOf(masterchef.address)
    senderBalBefore = threePoolVault.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)

    assert sdtToken.balanceOf(
        DEFAULT_DEPLOYER_ACCOUNT) == 1000000000000000000000

    masterchef.withdraw(0, 1000, sender)

    assert sdtToken.balanceOf(
        DEFAULT_DEPLOYER_ACCOUNT) > 1000000000000000000000

    masterchefBalAfter = threePoolVault.balanceOf(masterchef.address)
    senderBalAfter = threePoolVault.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)

    assert masterchefBalAfter == masterchefBalBefore - 1000
    assert senderBalAfter == senderBalBefore + 1000


def test_MasterChef_transferOwnership(deployedContracts):
    masterchef = deployedContracts['masterchef']
    threePoolVault = deployedContracts['threePoolVault']
    sender = deployedContracts['sender']
    sdtToken = deployedContracts['sdtToken']
    timelockGovernance = deployedContracts['timelockGovernance']

    masterchef.transferOwnership(timelockGovernance.address, sender)

    assert masterchef.owner() == timelockGovernance.address

    # add check that onlyOwner functions should fail if trx is sent via DEFAULT_DEPLOYER_ACCOUNT


################################## eursCrvVault tests #####################################


def test_eursCrvVault_token(deployedContracts):
    """
    Returns the unwrapped native token address that the Vault takes as deposit.
    """
    eursCrvVault = deployedContracts['eursCrvVault']
    eursCrv = deployedContracts['eursCrv']

    token = eursCrvVault.token()

    assert token == eursCrv.address


def test_eursCrvVault_name(deployedContracts):
    """
    Returns the vault’s wrapped token name as a string, e.g. “yearn Dai Stablecoin".
    """
    eursCrvVault = deployedContracts['eursCrvVault']
    eursCrv = deployedContracts['eursCrv']

    name = eursCrvVault.name()
    eursCrvName = eursCrv.name()

    assert name == "stake dao " + eursCrvName


def test_eursCrvVault_symbol(deployedContracts):
    """
    Returns the vault’s wrapped token symbol as a string, e.g. “yDai”.
    """
    eursCrvVault = deployedContracts['eursCrvVault']
    eursCrv = deployedContracts['eursCrv']

    symbol = eursCrvVault.symbol()
    eursCrvSymbol = eursCrv.symbol()

    assert symbol == "sd" + eursCrvSymbol


def test_eursCrvVault_decimals(deployedContracts):
    """
    Returns the amount of decimals for this vault’s wrapped token as a uint8.
    """
    eursCrvVault = deployedContracts['eursCrvVault']
    eursCrv = deployedContracts['eursCrv']

    decimals = eursCrvVault.decimals()
    eursCrvDecimals = eursCrv.decimals()

    assert decimals == eursCrvDecimals


def test_eursCrvVault_controller(deployedContracts):
    """
    Returns the address of the Vault's Controller.
    """
    eursCrvVault = deployedContracts['eursCrvVault']
    controller = deployedContracts['controller']

    threePoolVaultController = eursCrvVault.controller()

    assert controller.address == threePoolVaultController


def test_eursCrvVault_governance(deployedContracts):
    """
    Returns the address of the Vault’s governance contract.
    """
    eursCrvVault = deployedContracts['eursCrvVault']
    governanceGSPAddress = deployedContracts['governanceGSPAddress']

    threePoolVaultGovernance = eursCrvVault.governance()

    assert threePoolVaultGovernance == governanceGSPAddress


def test_eursCrvVault_deposit(deployedContracts):
    """
    Deposits token (same as want() returns) into a smart contact specified by the Strategy.
    """
    eursCrvVault = deployedContracts['eursCrvVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    eursCrv = deployedContracts['eursCrv']

    beforeSenderBal = eursCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = eursCrv.balanceOf(eursCrvVault.address)

    eursCrvVault.deposit(1, sender)

    afterSenderBal = eursCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = eursCrv.balanceOf(eursCrvVault.address)

    assert afterSenderBal == beforeSenderBal - 1
    assert afterVaultBal == beforeVaultBal + 1


def test_eursCrvVault_depositAll(deployedContracts):
    """
    Deposits token (same as want() returns) into a smart contact specified by the Strategy.
    """
    eursCrvVault = deployedContracts['eursCrvVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    eursCrv = deployedContracts['eursCrv']

    beforeSenderBal = eursCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = eursCrv.balanceOf(eursCrvVault.address)

    eursCrvVault.deposit(beforeSenderBal, sender)

    afterSenderBal = eursCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = eursCrv.balanceOf(eursCrvVault.address)

    assert afterSenderBal == 0
    assert afterVaultBal == beforeVaultBal + beforeSenderBal


def test_eursCrvVault_getPricePerFullShare(deployedContracts):
    """
    Returns the price of the Vault’s wrapped token, denominated in the unwrapped native token.
    The calculation is: nativeTokenBalance/yTokenTotalSupply

    Where nativeTokenBalance is the current balance of native token (e.g. DAI) in the Vault,
    Controller and Strategy contracts. And yTokenTotalSupply is the total supply of the Vault's
    wrapped Token (e.g. yDAI).
    """
    eursCrvVault = deployedContracts['eursCrvVault']
    pricePerFullShare = eursCrvVault.getPricePerFullShare()

    # TODO: Calculate it via above formula and then assert
    assert pricePerFullShare == 1000000000000000000


def test_eursCrvVault_withdraw(deployedContracts):
    """
    Partially withdraws funds (denominated in want() token) from the Strategy,
    and should always only be sending these to the Vault. In case the Strategy
    implements harvest(), a withdrawal fee may be applied. This function should
    have access control enforcing the Controller only to be its allowed caller.
    """
    eursCrvVault = deployedContracts['eursCrvVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    eursCrv = deployedContracts['eursCrv']

    beforeSenderBal = eursCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = eursCrv.balanceOf(eursCrvVault.address)

    eursCrvVault.withdraw(1, sender)

    afterSenderBal = eursCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = eursCrv.balanceOf(eursCrvVault.address)

    assert afterSenderBal == beforeSenderBal + 1
    assert afterVaultBal == beforeVaultBal - 1


def test_eursCrvVault_withdrawAll(deployedContracts):
    """
    Withdraws the entire amount of want() tokens available,
    and should always only be sending these to the Vault. This
    function should have access control enforcing the Controller
    only to be its allowed caller. Typically used when migrating
    strategies.

    The function typically uses withdraw() and performs a set of
    sequential function calls depending on the Strategy.

    If the Strategy implements liquidity pools or lending platforms,
    then withdrawal from these platforms should be performed until
    the Vault’s unwrapped token is delivered back to the vault.

    Returns a uint256 of the total amount withdrawn.
    """
    eursCrvVault = deployedContracts['eursCrvVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    eursCrv = deployedContracts['eursCrv']

    beforeSenderBal = eursCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = eursCrv.balanceOf(eursCrvVault.address)

    eursCrvVault.withdrawAll(sender)

    afterSenderBal = eursCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = eursCrv.balanceOf(eursCrvVault.address)

    assert afterVaultBal == 0
    assert afterSenderBal == beforeSenderBal + beforeVaultBal


def test_eursCrvVault_earn(deployedContracts):
    eursCrvVault = deployedContracts['eursCrvVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    eursCrv = deployedContracts['eursCrv']

    eursCrvBal = eursCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)

    eursCrv.approve(eursCrvVault.address, eursCrvBal, sender)
    eursCrvVault.deposit(eursCrvBal, sender)
    available = eursCrvVault.available()

    assert eursCrv.balanceOf(eursCrvVault.address) == eursCrvBal

    beforeVaultBal = eursCrv.balanceOf(eursCrvVault.address)

    eursCrvVault.earn(sender)

    afterVaultBal = eursCrv.balanceOf(eursCrvVault.address)

    assert afterVaultBal == beforeVaultBal - available


################################## strategyCurveEursCrvVoterProxy tests #####################################

def test_strategyCurveEursCrvVoterProxy_want(deployedContracts):
    """
    Returns the address of the unwrapped token that the Strategy takes as deposit.
    """

    strategyCurveEursCrvVoterProxy = deployedContracts['strategyCurveEursCrvVoterProxy']
    eursCrv = deployedContracts['eursCrv']

    want = strategyCurveEursCrvVoterProxy.want()

    assert want == eursCrv.address


def test_strategyCurveEursCrvVoterProxy_harvest(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts['strategyCurveEursCrvVoterProxy']
    STRATEGIST = deployedContracts['STRATEGIST']

    strategyCurveEursCrvVoterProxy.harvest({'from': STRATEGIST})


################################## threePoolVault tests #####################################


def test_threePoolVault_token(deployedContracts):
    """
    Returns the unwrapped native token address that the Vault takes as deposit.
    """
    threePoolVault = deployedContracts['threePoolVault']
    threeCrv = deployedContracts['threeCrv']

    token = threePoolVault.token()

    assert token == threeCrv.address


def test_threePoolVault_name(deployedContracts):
    """
    Returns the vault’s wrapped token name as a string, e.g. “yearn Dai Stablecoin".
    """
    threePoolVault = deployedContracts['threePoolVault']
    threeCrv = deployedContracts['threeCrv']

    name = threePoolVault.name()
    threeCrvName = threeCrv.name()

    assert name == "stake dao " + threeCrvName


def test_threePoolVault_symbol(deployedContracts):
    """
    Returns the vault’s wrapped token symbol as a string, e.g. “yDai”.
    """
    threePoolVault = deployedContracts['threePoolVault']
    threeCrv = deployedContracts['threeCrv']

    symbol = threePoolVault.symbol()
    threeCrvSymbol = threeCrv.symbol()

    assert symbol == "sd" + threeCrvSymbol


def test_threePoolVault_decimals(deployedContracts):
    """
    Returns the amount of decimals for this vault’s wrapped token as a uint8.
    """
    threePoolVault = deployedContracts['threePoolVault']
    threeCrv = deployedContracts['threeCrv']

    decimals = threePoolVault.decimals()
    threeCrvDecimals = threeCrv.decimals()

    assert decimals == threeCrvDecimals


def test_threePoolVault_controller(deployedContracts):
    """
    Returns the address of the Vault's Controller.
    """
    threePoolVault = deployedContracts['threePoolVault']
    controller = deployedContracts['controller']

    threePoolVaultController = threePoolVault.controller()

    assert controller.address == threePoolVaultController


def test_threePoolVault_governance(deployedContracts):
    """
    Returns the address of the Vault’s governance contract.
    """
    threePoolVault = deployedContracts['threePoolVault']
    governanceGSPAddress = deployedContracts['governanceGSPAddress']

    threePoolVaultGovernance = threePoolVault.governance()

    assert threePoolVaultGovernance == governanceGSPAddress


def test_threePoolVault_deposit(deployedContracts):
    """
    Deposits token (same as want() returns) into a smart contact specified by the Strategy.
    """
    threePoolVault = deployedContracts['threePoolVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    threeCrv = deployedContracts['threeCrv']

    beforeSenderBal = threeCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = threeCrv.balanceOf(threePoolVault.address)

    threePoolVault.deposit(1, sender)

    afterSenderBal = threeCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = threeCrv.balanceOf(threePoolVault.address)

    assert afterSenderBal == beforeSenderBal - 1
    assert afterVaultBal == beforeVaultBal + 1


def test_threePoolVault_depositAll(deployedContracts):
    """
    Deposits token (same as want() returns) into a smart contact specified by the Strategy.
    """
    threePoolVault = deployedContracts['threePoolVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    threeCrv = deployedContracts['threeCrv']

    beforeSenderBal = threeCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = threeCrv.balanceOf(threePoolVault.address)

    threePoolVault.deposit(beforeSenderBal, sender)

    afterSenderBal = threeCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = threeCrv.balanceOf(threePoolVault.address)

    assert afterSenderBal == 0
    assert afterVaultBal == beforeVaultBal + beforeSenderBal


def test_threePoolVault_getPricePerFullShare(deployedContracts):
    """
    Returns the price of the Vault’s wrapped token, denominated in the unwrapped native token.
    The calculation is: nativeTokenBalance/yTokenTotalSupply

    Where nativeTokenBalance is the current balance of native token (e.g. DAI) in the Vault,
    Controller and Strategy contracts. And yTokenTotalSupply is the total supply of the Vault's
    wrapped Token (e.g. yDAI).
    """
    threePoolVault = deployedContracts['threePoolVault']
    pricePerFullShare = threePoolVault.getPricePerFullShare()

    # TODO: Calculate it via above formula and then assert
    assert pricePerFullShare == 1000000000000000000


def test_threePoolVault_withdraw(deployedContracts):
    """
    Partially withdraws funds (denominated in want() token) from the Strategy,
    and should always only be sending these to the Vault. In case the Strategy
    implements harvest(), a withdrawal fee may be applied. This function should
    have access control enforcing the Controller only to be its allowed caller.
    """
    threePoolVault = deployedContracts['threePoolVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    threeCrv = deployedContracts['threeCrv']

    beforeSenderBal = threeCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = threeCrv.balanceOf(threePoolVault.address)

    threePoolVault.withdraw(1, sender)

    afterSenderBal = threeCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = threeCrv.balanceOf(threePoolVault.address)

    assert afterSenderBal == beforeSenderBal + 1
    assert afterVaultBal == beforeVaultBal - 1


def test_threePoolVault_withdrawAll(deployedContracts):
    """
    Withdraws the entire amount of want() tokens available,
    and should always only be sending these to the Vault. This
    function should have access control enforcing the Controller
    only to be its allowed caller. Typically used when migrating
    strategies.

    The function typically uses withdraw() and performs a set of
    sequential function calls depending on the Strategy.

    If the Strategy implements liquidity pools or lending platforms,
    then withdrawal from these platforms should be performed until
    the Vault’s unwrapped token is delivered back to the vault.

    Returns a uint256 of the total amount withdrawn.
    """
    threePoolVault = deployedContracts['threePoolVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    threeCrv = deployedContracts['threeCrv']

    beforeSenderBal = threeCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = threeCrv.balanceOf(threePoolVault.address)

    threePoolVault.withdrawAll(sender)

    afterSenderBal = threeCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = threeCrv.balanceOf(threePoolVault.address)

    assert afterVaultBal == 0
    assert afterSenderBal == beforeSenderBal + beforeVaultBal


def test_threePoolVault_earn(deployedContracts):
    threePoolVault = deployedContracts['threePoolVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    threeCrv = deployedContracts['threeCrv']

    threeCrvBal = threeCrv.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)

    threeCrv.approve(threePoolVault.address, threeCrvBal, sender)
    threePoolVault.deposit(threeCrvBal, sender)
    available = threePoolVault.available()

    assert threeCrv.balanceOf(threePoolVault.address) == threeCrvBal

    beforeVaultBal = threeCrv.balanceOf(threePoolVault.address)

    threePoolVault.earn(sender)

    afterVaultBal = threeCrv.balanceOf(threePoolVault.address)

    assert afterVaultBal == beforeVaultBal - available


################################## strategyCurve3CrvVoterProxy tests #####################################

def test_strategyCurve3CrvVoterProxy_want(deployedContracts):
    """
    Returns the address of the unwrapped token that the Strategy takes as deposit.
    """

    strategyCurve3CrvVoterProxy = deployedContracts['strategyCurve3CrvVoterProxy']
    threeCrv = deployedContracts['threeCrv']

    want = strategyCurve3CrvVoterProxy.want()

    assert want == threeCrv.address


def test_strategyCurve3CrvVoterProxy_harvest(deployedContracts):
    strategyCurve3CrvVoterProxy = deployedContracts['strategyCurve3CrvVoterProxy']
    STRATEGIST = deployedContracts['STRATEGIST']

    strategyCurve3CrvVoterProxy.harvest({'from': STRATEGIST})


################################## sbtcVault tests #####################################


def test_sbtcVault_token(deployedContracts):
    """
    Returns the unwrapped native token address that the Vault takes as deposit.
    """
    sbtcVault = deployedContracts['sbtcVault']
    sbtc = deployedContracts['sbtc']

    token = sbtcVault.token()

    assert token == sbtc.address


def test_sbtcVault_name(deployedContracts):
    """
    Returns the vault’s wrapped token name as a string, e.g. “yearn Dai Stablecoin".
    """
    sbtcVault = deployedContracts['sbtcVault']
    sbtc = deployedContracts['sbtc']

    name = sbtcVault.name()
    sbtcName = sbtc.name()

    assert name == "stake dao " + sbtcName


def test_sbtcVault_symbol(deployedContracts):
    """
    Returns the vault’s wrapped token symbol as a string, e.g. “yDai”.
    """
    sbtcVault = deployedContracts['sbtcVault']
    sbtc = deployedContracts['sbtc']

    symbol = sbtcVault.symbol()
    sbtcSymbol = sbtc.symbol()

    assert symbol == "sd" + sbtcSymbol


def test_sbtcVault_decimals(deployedContracts):
    """
    Returns the amount of decimals for this vault’s wrapped token as a uint8.
    """
    sbtcVault = deployedContracts['sbtcVault']
    sbtc = deployedContracts['sbtc']

    decimals = sbtcVault.decimals()
    sbtcDecimals = sbtc.decimals()

    assert decimals == sbtcDecimals


def test_sbtcVault_controller(deployedContracts):
    """
    Returns the address of the Vault's Controller.
    """
    sbtcVault = deployedContracts['sbtcVault']
    controller = deployedContracts['controller']

    sbtcVaultController = sbtcVault.controller()

    assert controller.address == sbtcVaultController


def test_sbtcVault_governance(deployedContracts):
    """
    Returns the address of the Vault’s governance contract.
    """
    sbtcVault = deployedContracts['sbtcVault']
    governanceGSPAddress = deployedContracts['governanceGSPAddress']

    sbtcVaultGovernance = sbtcVault.governance()

    assert sbtcVaultGovernance == governanceGSPAddress


def test_sbtcVault_deposit(deployedContracts):
    """
    Deposits token (same as want() returns) into a smart contact specified by the Strategy.
    """
    sbtcVault = deployedContracts['sbtcVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    sbtc = deployedContracts['sbtc']

    beforeSenderBal = sbtc.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = sbtc.balanceOf(sbtcVault.address)

    sbtcVault.deposit(1, sender)

    afterSenderBal = sbtc.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = sbtc.balanceOf(sbtcVault.address)

    assert afterSenderBal == beforeSenderBal - 1
    assert afterVaultBal == beforeVaultBal + 1


def test_sbtcVault_depositAll(deployedContracts):
    """
    Deposits token (same as want() returns) into a smart contact specified by the Strategy.
    """
    sbtcVault = deployedContracts['sbtcVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    sbtc = deployedContracts['sbtc']

    beforeSenderBal = sbtc.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = sbtc.balanceOf(sbtcVault.address)

    sbtcVault.deposit(beforeSenderBal, sender)

    afterSenderBal = sbtc.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = sbtc.balanceOf(sbtcVault.address)

    assert afterSenderBal == 0
    assert afterVaultBal == beforeVaultBal + beforeSenderBal


def test_sbtcVault_getPricePerFullShare(deployedContracts):
    """
    Returns the price of the Vault’s wrapped token, denominated in the unwrapped native token.
    The calculation is: nativeTokenBalance/yTokenTotalSupply

    Where nativeTokenBalance is the current balance of native token (e.g. DAI) in the Vault,
    Controller and Strategy contracts. And yTokenTotalSupply is the total supply of the Vault's
    wrapped Token (e.g. yDAI).
    """
    sbtcVault = deployedContracts['sbtcVault']
    pricePerFullShare = sbtcVault.getPricePerFullShare()

    # TODO: Calculate it via above formula and then assert
    assert pricePerFullShare == 1000000000000000000


def test_sbtcVault_withdraw(deployedContracts):
    """
    Partially withdraws funds (denominated in want() token) from the Strategy,
    and should always only be sending these to the Vault. In case the Strategy
    implements harvest(), a withdrawal fee may be applied. This function should
    have access control enforcing the Controller only to be its allowed caller.
    """
    sbtcVault = deployedContracts['sbtcVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    sbtc = deployedContracts['sbtc']

    beforeSenderBal = sbtc.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = sbtc.balanceOf(sbtcVault.address)

    sbtcVault.withdraw(1, sender)

    afterSenderBal = sbtc.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = sbtc.balanceOf(sbtcVault.address)

    assert afterSenderBal == beforeSenderBal + 1
    assert afterVaultBal == beforeVaultBal - 1


def test_sbtcVault_withdrawAll(deployedContracts):
    """
    Withdraws the entire amount of want() tokens available,
    and should always only be sending these to the Vault. This
    function should have access control enforcing the Controller
    only to be its allowed caller. Typically used when migrating
    strategies.

    The function typically uses withdraw() and performs a set of
    sequential function calls depending on the Strategy.

    If the Strategy implements liquidity pools or lending platforms,
    then withdrawal from these platforms should be performed until
    the Vault’s unwrapped token is delivered back to the vault.

    Returns a uint256 of the total amount withdrawn.
    """
    sbtcVault = deployedContracts['sbtcVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    sbtc = deployedContracts['sbtc']

    beforeSenderBal = sbtc.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    beforeVaultBal = sbtc.balanceOf(sbtcVault.address)

    sbtcVault.withdrawAll(sender)

    afterSenderBal = sbtc.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)
    afterVaultBal = sbtc.balanceOf(sbtcVault.address)

    assert afterVaultBal == 0
    assert afterSenderBal == beforeSenderBal + beforeVaultBal


def test_sbtcVault_earn(deployedContracts):
    sbtcVault = deployedContracts['sbtcVault']
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    sbtc = deployedContracts['sbtc']

    sbtcBal = sbtc.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)

    sbtc.approve(sbtcVault.address, sbtcBal, sender)
    sbtcVault.deposit(sbtcBal, sender)
    available = sbtcVault.available()

    assert sbtc.balanceOf(sbtcVault.address) == sbtcBal

    beforeVaultBal = sbtc.balanceOf(sbtcVault.address)

    sbtcVault.earn(sender)

    afterVaultBal = sbtc.balanceOf(sbtcVault.address)

    assert afterVaultBal == beforeVaultBal - available


################################## StrategyCurveBTCVoterProxy tests #####################################


def test_strategyCurveBTCVoterProxy_want(deployedContracts):
    """
    Returns the address of the unwrapped token that the Strategy takes as deposit.
    """

    strategyCurveBTCVoterProxy = deployedContracts['strategyCurveBTCVoterProxy']
    sbtc = deployedContracts['sbtc']

    want = strategyCurveBTCVoterProxy.want()

    assert want == sbtc.address


def test_strategyCurveBTCVoterProxy_harvest(deployedContracts):
    strategyCurveBTCVoterProxy = deployedContracts['strategyCurveBTCVoterProxy']
    STRATEGIST = deployedContracts['STRATEGIST']

    strategyCurveBTCVoterProxy.harvest({'from': STRATEGIST})


################################## Controller tests #####################################

def test_controller_inCaseStrategyTokenGetStuck_strategyCurve3CrvVoterProxy(deployedContracts):
    """
    This controller function calls withdraw(IERC20 _asset)

    withdraw(IERC20 _asset):

    Dust collecting function to create additional rewards out of
    tokens that were incorrectly sent to the Strategy.

    Takes an ERC20 token address and should send the full amount
    of any such tokens in the Strategy to the Controller.

    This function should have access control enforcing the Controller
    only to be its allowed caller, and checks in place to ensure that
    the token types to withdraw are not those used by the Strategy.
    """
    strategyCurve3CrvVoterProxy = deployedContracts['strategyCurve3CrvVoterProxy']
    controller = deployedContracts['controller']
    sbtc = deployedContracts['sbtc']
    sender = deployedContracts['sender']
    STRATEGIST = deployedContracts['STRATEGIST']

    # Send some sBTC token to the strategyCurve3CrvVoterProxy
    sbtc.transfer(strategyCurve3CrvVoterProxy.address, 1, sender)

    balBefore = sbtc.balanceOf(controller.address)

    # Get the token out of strategyCurve3CrvVoterProxy to Controller
    controller.inCaseStrategyTokenGetStuck(
        strategyCurve3CrvVoterProxy.address, sbtc.address, {'from': STRATEGIST})

    balAfter = sbtc.balanceOf(controller.address)

    assert balAfter == balBefore + 1


def test_controller_inCaseStrategyTokenGetStuck_strategyCurveEursCrvVoterProxy(deployedContracts):
    """
    This controller function calls withdraw(IERC20 _asset)

    withdraw(IERC20 _asset):

    Dust collecting function to create additional rewards out of
    tokens that were incorrectly sent to the Strategy.

    Takes an ERC20 token address and should send the full amount
    of any such tokens in the Strategy to the Controller.

    This function should have access control enforcing the Controller
    only to be its allowed caller, and checks in place to ensure that
    the token types to withdraw are not those used by the Strategy.
    """
    strategyCurveEursCrvVoterProxy = deployedContracts['strategyCurveEursCrvVoterProxy']
    controller = deployedContracts['controller']
    sbtc = deployedContracts['sbtc']
    sender = deployedContracts['sender']
    STRATEGIST = deployedContracts['STRATEGIST']

    # Send some sBTC token to the strategyCurveEursCrvVoterProxy
    sbtc.transfer(strategyCurveEursCrvVoterProxy.address, 1, sender)

    balBefore = sbtc.balanceOf(controller.address)

    # Get the token out of strategyCurveEursCrvVoterProxy to Controller
    controller.inCaseStrategyTokenGetStuck(
        strategyCurveEursCrvVoterProxy.address, sbtc.address, {'from': STRATEGIST})

    balAfter = sbtc.balanceOf(controller.address)

    assert balAfter == balBefore + 1


def test_controller_inCaseStrategyTokenGetStuck_strategyCurveBTCVoterProxy(deployedContracts):
    """
    This controller function calls withdraw(IERC20 _asset)

    withdraw(IERC20 _asset):

    Dust collecting function to create additional rewards out of
    tokens that were incorrectly sent to the Strategy.

    Takes an ERC20 token address and should send the full amount
    of any such tokens in the Strategy to the Controller.

    This function should have access control enforcing the Controller
    only to be its allowed caller, and checks in place to ensure that
    the token types to withdraw are not those used by the Strategy.
    """
    strategyCurveBTCVoterProxy = deployedContracts['strategyCurveBTCVoterProxy']
    controller = deployedContracts['controller']
    threeCrv = deployedContracts['threeCrv']
    sender = deployedContracts['sender']
    STRATEGIST = deployedContracts['STRATEGIST']

    # Send some threeCrv token to the strategyCurveBTCVoterProxy
    threeCrv.transfer(strategyCurveBTCVoterProxy.address, 1, sender)

    balBefore = threeCrv.balanceOf(controller.address)

    # Get the token out of strategyCurveBTCVoterProxy to Controller
    controller.inCaseStrategyTokenGetStuck(
        strategyCurveBTCVoterProxy.address, threeCrv.address, {'from': STRATEGIST})

    balAfter = threeCrv.balanceOf(controller.address)

    assert balAfter == balBefore + 1


################################## veCurveVault tests #####################################

def test_veCurveVault_deposit(deployedContracts):
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    crv = deployedContracts['crv']
    crvBal = deployedContracts['crvBal']
    veCurve = deployedContracts['veCurve']

    crv.approve(veCurve.address, crvBal, sender)

    veCurve.depositAll(sender)

    depositBal = veCurve.balanceOf(DEFAULT_DEPLOYER_ACCOUNT)

    assert crvBal == depositBal


def test_veCurveVault_claim(deployedContracts):
    sender = deployedContracts['sender']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    veCurve = deployedContracts['veCurve']

    veCurve.claim(sender)
