import {HardhatUserConfig} from 'hardhat/config';
import '@nomiclabs/hardhat-ethers';
import '@nomiclabs/hardhat-waffle';
import '@nomiclabs/hardhat-etherscan';
import 'hardhat-tracer';
import "hardhat-typechain";

// import './tasks/deploy-usd';
// import './tasks/deploy-btc';
// import './tasks/deploy-eur';
// import './tasks/deploy-am-3crv';

require('dotenv').config();

const DEPLOYER = process.env.DEPLOYER;

export default {
  defaultNetwork: 'hardhat',
  networks: {
    hardhat: {
      forking: {
        url: process.env.ALCHEMY_MAINNET
        // url: '<your-rpc-url-to-connect-to-matic-node>'
      }
    },
    mainnet: {
      url: process.env.ALCHEMY_MAINNET,
      // accounts: [`0x${DEPLOYER}`]
    },
    matic: {
      url: `<your-rpc-url-to-connect-to-matic-node>`,
      // accounts: [`0x${DEPLOYER}`],
      gasPrice: 9000000000
    }
  },
  solidity: {
    compilers: [
      {version: '0.8.0'},
      {version: '0.7.4'},
      {version: '0.6.12'},
      {version: '0.5.17'}
    ]
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_KEY
  }
} as HardhatUserConfig;
