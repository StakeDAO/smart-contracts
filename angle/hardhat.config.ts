import { HardhatUserConfig } from "hardhat/config";
import "@nomiclabs/hardhat-waffle";
import "@nomiclabs/hardhat-etherscan";
import "@nomiclabs/hardhat-vyper";
import "hardhat-gas-reporter";
import "solidity-coverage";
import "hardhat-deploy";
import "hardhat-deploy-ethers";
import "hardhat-contract-sizer";
import "./tasks/global";

require("dotenv").config();

export default {
  defaultNetwork: "hardhat",
  networks: {
    hardhat: {
      forking: {
        url: process.env.MAINNET,
        blockNumber: 14036501
      }
    },
    mainnet: {
      url: process.env.MAINNET,
      accounts: [`0x${process.env.DEPLOYER_PKEY}`],
      gasPrice: 120000000000
    }
  },
  namedAccounts: {
    deployer: 0
  },
  vyper: {
    version: "0.2.7"
  },
  solidity: {
    compilers: [{ version: "0.8.2" }, { version: "0.7.4" }, { version: "0.6.12" }, { version: "0.5.17" }],
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_KEY
  },
  contractSizer: {
    alphaSort: true,
    disambiguatePaths: false,
    runOnCompile: true,
    strict: false
  },
  gasReporter: {
    currency: "USD",
    coinmarketcap: process.env.COINMARKETCAP_KEY
  }
} as HardhatUserConfig;
