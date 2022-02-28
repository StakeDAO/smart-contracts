import pytest

strategyNames = [
    "StrategyCurveAm3Crv"
]

@pytest.mark.parametrize("strategyName", strategyNames)
def test_polygon_vault_deposit(curveConfig, strategyName, deployerAccount):
    token = curveConfig[strategyName]['vaultToken']
    vault = curveConfig[strategyName]['vault']
    gauge = curveConfig[strategyName]['gauge']

    amount = 100_000*10**18
    verifyDeposit(amount, vault, deployerAccount, gauge, token)

@pytest.mark.parametrize("strategyName", strategyNames)
def test_polygon_vault_withdraw(curveConfig, strategyName, deployerAccount):
    token = curveConfig[strategyName]['vaultToken']
    vault = curveConfig[strategyName]['vault']
    gauge = curveConfig[strategyName]['gauge']

    amount = 100_000*10**18
    verifyDeposit(amount, vault, deployerAccount, gauge, token)
    verifyWithdraw(vault, token, deployerAccount)

@pytest.mark.parametrize("strategyName", strategyNames)
def test_polygon_vault_earn(curveConfig, strategyName, deployerAccount):
    token = curveConfig[strategyName]['vaultToken']
    vault = curveConfig[strategyName]['vault']
    strategy = curveConfig[strategyName]['strategy']
    gauge = curveConfig[strategyName]['gauge']

    amount = 100_000*10**18
    verifyDeposit(amount, vault, deployerAccount, gauge, token)
    verifyEarn(strategy, vault, deployerAccount)

@pytest.mark.parametrize("strategyName", strategyNames)
def test_polygon_strategy_whale_process(curveConfig, strategyName, deployerAccount):
    token = curveConfig[strategyName]['vaultToken']
    vault = curveConfig[strategyName]['vault']
    strategy = curveConfig[strategyName]['strategy']
    gauge = curveConfig[strategyName]['gauge']
    amount = 100_000_000_000 * 10**18

    verifyDeposit(amount, vault, deployerAccount, gauge, token)
    verifyEarn(strategy, vault, deployerAccount)
    verifyWithdraw(vault, token, deployerAccount)

def seedAccount(token, approvalAccount, amount, receivingAccount, gauge):
    token.approve(approvalAccount, amount, {'from': receivingAccount})
    token.transfer(receivingAccount, amount, {'from': gauge})

def verifyDeposit(amount, vault, deployerAccount, gauge, token):
    seedAccount(token, vault, amount, deployerAccount, gauge)

    senderShareBefore = vault.balanceOf(deployerAccount)
    senderBalanceBefore = token.balanceOf(deployerAccount)
    vaultBalanceBefore = token.balanceOf(vault.address)

    token.approve(vault, senderBalanceBefore, {'from': deployerAccount})
    vault.deposit(senderBalanceBefore, {'from': deployerAccount})

    senderShareAfter = vault.balanceOf(deployerAccount)
    senderBalanceAfter = token.balanceOf(deployerAccount)
    vaultBalanceAfter = token.balanceOf(vault.address)

    assert senderShareAfter - senderShareBefore > 0
    assert senderBalanceBefore - senderBalanceAfter > 0
    assert senderBalanceBefore - senderBalanceAfter == vaultBalanceAfter - vaultBalanceBefore

def verifyWithdraw(vault, token, deployerAccount):
    senderShareBefore = vault.balanceOf(deployerAccount)
    senderBalanceBefore = token.balanceOf(deployerAccount)
    vaultBalanceBefore = token.balanceOf(vault.address)

    vault.withdraw(vaultBalanceBefore, {'from': deployerAccount})

    senderShareAfter = vault.balanceOf(deployerAccount)
    senderBalanceAfter = token.balanceOf(deployerAccount)
    vaultBalanceAfter = token.balanceOf(vault.address)

    assert senderShareAfter - senderShareBefore < 0
    assert senderBalanceBefore - senderBalanceAfter < 0
    assert senderBalanceBefore - senderBalanceAfter == vaultBalanceAfter - vaultBalanceBefore

def verifyEarn(strategy, vault, deployerAccount):
    strategyBalanceBefore = strategy.balanceOf()
    totalBalanceBefore = vault.balance()

    vault.earn({'from': deployerAccount})

    strategyBalanceAfter = strategy.balanceOf()
    totalBalanceAfter = vault.balance()

    assert strategyBalanceAfter > strategyBalanceBefore
    assert totalBalanceAfter == totalBalanceBefore
    