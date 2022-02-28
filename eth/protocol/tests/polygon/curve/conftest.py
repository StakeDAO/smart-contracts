import pytest
from brownie import (
    Controller,
    StrategyCurveAm3Crv,
    GaugeV2,
    yVault,
    Token,
    accounts
)
import json

STRATEGIES = [
    StrategyCurveAm3Crv
]

@pytest.fixture(scope="module", autouse=True)
def polygon_config():
    config = open("config.json", "r")
    try:
        configData = json.loads(config.read())
    except:
        configData = {}

    return configData['polygon']

@pytest.fixture(scope="module", autouse=True)
def deployerAccount():
    return accounts[0]

@pytest.fixture(scope="module", autouse=True)
def controller(deployerAccount):
    return Controller.deploy(deployerAccount, {'from': deployerAccount})

@pytest.fixture(scope="module", autouse=True)
def curveConfig(polygon_config, deployerAccount, controller):
    curveConfiguration = {}

    strategyDictionary = {
        'StrategyCurveAm3Crv': StrategyCurveAm3Crv
    }

    for key, value in polygon_config['strategies'].items():
        strategy = strategyDictionary[key].deploy(controller, {'from': deployerAccount})
        vaultTokenAddress = value['vaultToken']
        vaultToken = Token.at(vaultTokenAddress)
        vault = yVault.deploy(vaultToken, controller, deployerAccount, {'from': deployerAccount})
        gauge = GaugeV2.at(value['gaugeAddress'])
        curveConfiguration[key] = {}
        curveConfiguration[key]['strategy'] = strategy
        curveConfiguration[key]['vaultTokenAddress'] = vaultTokenAddress
        curveConfiguration[key]['vaultToken'] = vaultToken
        curveConfiguration[key]['vault'] = vault
        curveConfiguration[key]['gauge'] = gauge

        setStrategy(controller, vaultTokenAddress, strategy, vault, deployerAccount)

    return curveConfiguration

def setStrategy(controller, vaultTokenAddress, strategy, vault, deployerAccount):
    controller.setVault(vaultTokenAddress, vault, {'from': deployerAccount})
    controller.approveStrategy(vaultTokenAddress, strategy, {'from': deployerAccount})
    controller.setStrategy(vaultTokenAddress, strategy, {'from': deployerAccount})
