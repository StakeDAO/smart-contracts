import {HardhatUserConfig} from 'hardhat/config';
import '@nomiclabs/hardhat-ethers';
import '@nomiclabs/hardhat-waffle';
import '@nomiclabs/hardhat-etherscan';
import 'hardhat-tracer';

import './tasks/deploy-usd';
import './tasks/deploy-btc';
import './tasks/deploy-eur';
import './tasks/deploy-frx';
import './tasks/deploy-steth';

require('dotenv').config();

const DEPLOYER = process.env.DEPLOYER;

export default {
	defaultNetwork: 'hardhat',
	networks: {
		hardhat: {
			forking: {
				url: process.env.ALCHEMY_MAINNET,
			},
		},
		mainnet: {
			url: process.env.ALCHEMY_MAINNET,
			accounts: [`0x${DEPLOYER}`],
			gasPrice: 60000000000,
		},
	},
	solidity: {
		compilers: [
			{version: '0.8.0'},
			{version: '0.7.4'},
			{version: '0.6.12'},
			{version: '0.5.17'},
		],
	},
	etherscan: {
		apiKey: process.env.ETHERSCAN_KEY,
	},
} as HardhatUserConfig;
