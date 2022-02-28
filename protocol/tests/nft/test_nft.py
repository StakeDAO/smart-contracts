import pytest
from brownie import *
import typer
import json
import brownie


@pytest.fixture(scope="module", autouse=True)
def deployedContracts():

    deployed = open("config.json", "r")

    try:
        deployed = json.loads(deployed.read())
    except:
        deployed = {}

    ENV = ""
    if (network.chain.id == 1):
        ENV = "prod"
    else:
        ENV = "dev"

    # account used for executing transactions
    DEFAULT_DEPLOYER_ACCOUNT = accounts[0]

    GNOSIS_SAFE_PROXY = deployed[ENV]['GNOSIS_SAFE_PROXY']

    TREASURY_VAULT = deployed[ENV]['TREASURY_VAULT']
    treasuryVault = Contract(TREASURY_VAULT)

    SDT = deployed[ENV]['SDT']
    sdt = Contract(SDT)

    xsdt = Contract(deployed[ENV]['SANCTUARY'])

    SBTC_CRV = deployed[ENV]['SBTC_CRV']

    THREE_CRV = deployed[ENV]['THREE_CRV']

    EURS_CRV = deployed[ENV]['EURS_CRV']

    DAI = deployed[ENV]['DAI']
    dai = Contract(DAI)

    VESTING_ESCROW = deployed[ENV]['VESTING_ESCROW']

    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

    SDT_STAKE_AMOUNT = 100*10**18

    deployer = {'from': DEFAULT_DEPLOYER_ACCOUNT}

    multisig = {'from': GNOSIS_SAFE_PROXY}

    # deploy NFT contract
    nft = StakeDaoNFT.deploy(ZERO_ADDRESS, deployer)

    # deploy StakeDaoNFTPalace
    nftPalace = StakeDaoNFTPalace.deploy(nft.address, xsdt.address, deployer)

    # give StakeDaoNFTPalace a minter role
    nft.addMinter(nftPalace.address, deployer)

    XSDT_WHALE = '0x40ec5B33f54e0E8A33A975908C5BA1c14e5BbbDf'
    xsdt_whale = {'from': XSDT_WHALE}

    xsdt.transfer(accounts[1], 2 * 10**22, xsdt_whale)
    xsdt.transfer(accounts[2], 2 * 10**22, xsdt_whale)
    xsdt.transfer(accounts[3], 3 * 10**22, xsdt_whale)
    xsdt.transfer(accounts[4], 8 * 10**22, xsdt_whale)

    return {"dai": dai, "treasuryVault": treasuryVault, "multisig": multisig, "deployer": deployer, "DAI": DAI, "SDT": SDT, "SBTC_CRV": SBTC_CRV, "THREE_CRV": THREE_CRV, "EURS_CRV": EURS_CRV, "SDT_STAKE_AMOUNT": SDT_STAKE_AMOUNT, "sdt": sdt, "xsdt": xsdt, "nft": nft, "nftPalace": nftPalace, "VESTING_ESCROW": VESTING_ESCROW}


def test_create_id(deployedContracts):
    deployer = deployedContracts["deployer"]
    xsdt = deployedContracts['xsdt']
    sdt = deployedContracts['sdt']
    nft = deployedContracts['nft']
    nftPalace = deployedContracts['nftPalace']

    for i in range(1, 112):
        tx = nft.create(1, 0, "", "", deployer)
        id = tx.return_value
        assert id == i


def test_add_card_cost(deployedContracts):
    deployer = deployedContracts["deployer"]
    xsdt = deployedContracts['xsdt']
    sdt = deployedContracts['sdt']
    nft = deployedContracts['nft']
    nftPalace = deployedContracts['nftPalace']

    for i in range(1, 112):
        if i <= 100:
            nftPalace.addCard(i, 400 * 10**18, deployer)
            assert nftPalace.cards(i) == 400 * 10**18
        elif i <= 110:
            nftPalace.addCard(i, 1250 * 10**18, deployer)
            assert nftPalace.cards(i) == 1250 * 10**18
        else:
            nftPalace.addCard(i, 5000 * 10**18, deployer)
            assert nftPalace.cards(i) == 5000 * 10**18


def test_xsdt_stake(deployedContracts):
    deployer = deployedContracts["deployer"]
    xsdt = deployedContracts['xsdt']
    sdt = deployedContracts['sdt']
    nft = deployedContracts['nft']
    nftPalace = deployedContracts['nftPalace']

    XSDT_WHALE = '0xdca628ce9699500191c37d6a4d029bac9ae76447'
    xsdt_whale = {'from': XSDT_WHALE}

    xsdt.approve(nftPalace.address, 10**9 * 10**18, {'from': accounts[1]})
    nftPalace.stake(1000 * 10**18, {'from': accounts[1]})
    assert nftPalace.balanceOf(accounts[1]) == 1000 * 10**18

    xsdt.approve(nftPalace.address, 10**9 * 10**18, {'from': accounts[2]})
    nftPalace.stake(5000 * 10**18, {'from': accounts[2]})
    assert nftPalace.balanceOf(accounts[2]) == 5000 * 10**18

    xsdt.approve(nftPalace.address, 10**9 * 10**18, {'from': accounts[3]})
    nftPalace.stake(20000 * 10**18, {'from': accounts[3]})
    assert nftPalace.balanceOf(accounts[3]) == 20000 * 10**18

    xsdt.approve(nftPalace.address, 10**9 * 10**18, {'from': accounts[4]})
    nftPalace.stake(75000 * 10**18, {'from': accounts[4]})
    assert nftPalace.balanceOf(accounts[4]) == 75000 * 10**18


def test_nft_redeem_fail_with_insufficient_points(deployedContracts):
    deployer = deployedContracts["deployer"]
    xsdt = deployedContracts['xsdt']
    sdt = deployedContracts['sdt']
    nft = deployedContracts['nft']
    nftPalace = deployedContracts['nftPalace']

    print("points [1]", nftPalace.earned(accounts[1]) / 10**18)
    with brownie.reverts("Not enough points to redeem for card"):
        nftPalace.redeem(55, {'from': accounts[1]})
    assert nft.balanceOf(accounts[1], 55) == 0


def test_nft_redeem(deployedContracts):
    deployer = deployedContracts["deployer"]
    xsdt = deployedContracts['xsdt']
    sdt = deployedContracts['sdt']
    nft = deployedContracts['nft']
    nftPalace = deployedContracts['nftPalace']

    # for i in range(1, 24):
    #     chain.sleep(86400)
    #     chain.mine(1)
    #     print("Day", i)
    #     print(nftPalace.earned(accounts[1]) / 10**18)
    #     print(nftPalace.earned(accounts[2]) / 10**18)
    #     print(nftPalace.earned(accounts[3]) / 10**18)
    #     print(nftPalace.earned(accounts[4]) / 10**18)

    # 1.5 days later
    chain.sleep(129600)
    chain.mine(1)

    print("points 1.4", nftPalace.earned(accounts[4]) / 10**18)
    nftPalace.redeem(55, {'from': accounts[4]})
    assert nft.balanceOf(accounts[4], 55) == 1
    print("URI", nft.uri(55))

    # 0.5 days later
    chain.sleep(43200)
    chain.mine(1)

    print("points 2.3", nftPalace.earned(accounts[3]) / 10**18)
    nftPalace.redeem(7, {'from': accounts[3]})
    assert nft.balanceOf(accounts[3], 7) == 1
    print("URI", nft.uri(7))

    # 1.8 days later
    chain.sleep(155520)
    chain.mine(1)

    print("points 3.2", nftPalace.earned(accounts[2]) / 10**18)
    nftPalace.redeem(88, {'from': accounts[2]})
    assert nft.balanceOf(accounts[2], 88) == 1
    print("URI", nft.uri(88))

    # 1.7 days later
    chain.sleep(146880)
    chain.mine(1)

    print("points 4.4", nftPalace.earned(accounts[4]) / 10**18)
    nftPalace.redeem(101, {'from': accounts[4]})
    assert nft.balanceOf(accounts[4], 101) == 1
    print("URI", nft.uri(101))

    # 2.6 days later
    chain.sleep(224640)
    chain.mine(1)

    print("points 5.3", nftPalace.earned(accounts[3]) / 10**18)
    nftPalace.redeem(107, {'from': accounts[3]})
    assert nft.balanceOf(accounts[3], 107) == 1
    print("URI", nft.uri(107))

    # 8 days later
    chain.sleep(8 * 86400)
    chain.mine(1)

    print("points 6.2", nftPalace.earned(accounts[2]) / 10**18)
    nftPalace.redeem(110, {'from': accounts[2]})
    assert nft.balanceOf(accounts[2], 110) == 1
    print("URI", nft.uri(110))

    # 0 days later
    # chain.sleep(2 * 86400)
    chain.mine(1)

    print("points 7.1", nftPalace.earned(accounts[1]) / 10**18)
    nftPalace.redeem(99, {'from': accounts[1]})
    assert nft.balanceOf(accounts[1], 99) == 1
    print("URI", nft.uri(99))

    # 6 days later
    chain.sleep(6 * 86400)
    chain.mine(1)
    chain.snapshot()

    print("points 8.4", nftPalace.earned(accounts[4]) / 10**18)
    nftPalace.redeem(111, {'from': accounts[4]})
    assert nft.balanceOf(accounts[4], 111) == 1
    print("URI", nft.uri(111))

    chain.revert()
    # 8.4 days later
    chain.sleep(725760)
    chain.mine(1)
    chain.snapshot()

    print("points 9.3", nftPalace.earned(accounts[3]) / 10**18)
    nftPalace.redeem(111, {'from': accounts[3]})
    assert nft.balanceOf(accounts[3], 111) == 1
    print("URI", nft.uri(111))

    chain.revert()
    # 33 days later
    chain.sleep(33 * 86400)
    chain.mine(1)
    chain.snapshot()

    print("points 10.2", nftPalace.earned(accounts[2]) / 10**18)
    nftPalace.redeem(111, {'from': accounts[2]})
    assert nft.balanceOf(accounts[2], 111) == 1
    print("URI", nft.uri(111))

    chain.revert()
    # 0 days later
    # chain.sleep(0)
    chain.mine(1)

    print("points 11.1", nftPalace.earned(accounts[1]) / 10**18)
    nftPalace.redeem(103, {'from': accounts[1]})
    assert nft.balanceOf(accounts[1], 103) == 1
    print("URI", nft.uri(103))

    # 181 days later
    chain.sleep(15638400)
    chain.mine(1)

    print("points 12.1", nftPalace.earned(accounts[1]) / 10**18)
    nftPalace.redeem(111, {'from': accounts[1]})
    assert nft.balanceOf(accounts[1], 111) == 1
    print("URI", nft.uri(111))


def test_nft_failed_re_redeem(deployedContracts):
    deployer = deployedContracts["deployer"]
    xsdt = deployedContracts['xsdt']
    sdt = deployedContracts['sdt']
    nft = deployedContracts['nft']
    nftPalace = deployedContracts['nftPalace']

    print("points [4]", nftPalace.earned(accounts[4]) / 10**18)
    with brownie.reverts("Max cards minted"):
        nftPalace.redeem(111, {'from': accounts[4]})
    assert nft.balanceOf(accounts[4], 111) == 0


def test_nft_redeem_fail_on_uncreated_card(deployedContracts):
    deployer = deployedContracts["deployer"]
    xsdt = deployedContracts['xsdt']
    sdt = deployedContracts['sdt']
    nft = deployedContracts['nft']
    nftPalace = deployedContracts['nftPalace']

    print("points [4]", nftPalace.earned(accounts[4]) / 10**18)
    with brownie.reverts("Card not found"):
        nftPalace.redeem(222, {'from': accounts[4]})
    assert nft.balanceOf(accounts[4], 222) == 0


def test_nft_redeem_for_whale_exiting_before_redeem(deployedContracts):
    deployer = deployedContracts["deployer"]
    xsdt = deployedContracts['xsdt']
    sdt = deployedContracts['sdt']
    nft = deployedContracts['nft']
    nftPalace = deployedContracts['nftPalace']
    VESTING_ESCROW = deployedContracts['VESTING_ESCROW']

    sdt.transfer(accounts[5], 10**24, {'from': VESTING_ESCROW})
    sdt.approve(xsdt.address, 10**9 * 10**18, {'from': accounts[5]})
    xsdt.enter(10**24, {'from': accounts[5]})

    xsdt.approve(nftPalace.address, 10**9 * 10**18, {'from': accounts[5]})
    nftPalace.stake(xsdt.balanceOf(accounts[5]), {'from': accounts[5]})

    chain.sleep(4 * 86400)
    chain.mine(1)
    print("points [5]", nftPalace.earned(accounts[5]) / 10**18)

    nftPalace.exit({'from': accounts[5]})

    chain.sleep(3600)
    chain.mine(1)
    print("points [5]", nftPalace.earned(accounts[5]) / 10**18)
    nftPalace.redeem(109, {'from': accounts[5]})
    assert nft.balanceOf(accounts[5], 109) == 1


def test_xsdt_withdraw(deployedContracts):
    deployer = deployedContracts["deployer"]
    xsdt = deployedContracts['xsdt']
    sdt = deployedContracts['sdt']
    nft = deployedContracts['nft']
    nftPalace = deployedContracts['nftPalace']

    before = xsdt.balanceOf(accounts[1])
    nftPalace.withdraw(60 * 10**18, {'from': accounts[1]})
    after = xsdt.balanceOf(accounts[1])

    assert nftPalace.balanceOf(accounts[1]) == 940 * 10**18
    assert after - before == 60 * 10**18


def test_exit(deployedContracts):
    deployer = deployedContracts["deployer"]
    xsdt = deployedContracts['xsdt']
    sdt = deployedContracts['sdt']
    nft = deployedContracts['nft']
    nftPalace = deployedContracts['nftPalace']

    XSDT_WHALE = '0xdca628ce9699500191c37d6a4d029bac9ae76447'
    xsdt_whale = {'from': XSDT_WHALE}

    before = xsdt.balanceOf(accounts[3])
    nftPalace.exit({'from': accounts[3]})
    after = xsdt.balanceOf(accounts[3])

    assert nftPalace.balanceOf(accounts[3]) == 0
    assert after - before == 20000 * 10**18


def test_set_nft(deployedContracts):
    deployer = deployedContracts["deployer"]
    xsdt = deployedContracts['xsdt']
    sdt = deployedContracts['sdt']
    nft = deployedContracts['nft']
    nftPalace = deployedContracts['nftPalace']

    nftPalace.setNFT("0xe4605d46Fd0B3f8329d936a8b258D69276cBa264", deployer)
    assert nftPalace.nft() == "0xe4605d46Fd0B3f8329d936a8b258D69276cBa264"
