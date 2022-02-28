import { HardhatUserConfig } from "hardhat/config";
import "@nomiclabs/hardhat-waffle";
import "@nomiclabs/hardhat-etherscan";
import "@nomiclabs/hardhat-vyper";

import "hardhat-deploy";
import "hardhat-deploy-ethers";
import "./tasks/global";

require("dotenv").config();

const TESTING_DEPLOYER_PKEY = process.env.TESTING_DEPLOYER_PKEY;

export default {
	defaultNetwork: "hardhat",
	networks: {
		harmony: {
			url: `https://api.harmony.one`,
			accounts: [`0x${TESTING_DEPLOYER_PKEY}`]
		},
	},
	namedAccounts: {
		deployer: 0,
	},
	vyper: {
		version: "0.2.7",
	},
	solidity: {
		compilers: [{ version: "0.8.0" }, { version: "0.7.4" }, { version: "0.6.12" }, { version: "0.5.17" }],
		settings: {
			optimizer: {
				enabled: true,
				runs: 200,
			},
		},
	},
	etherscan: {
		apiKey: process.env.ETHERSCAN_KEY,
	},
} as HardhatUserConfig;