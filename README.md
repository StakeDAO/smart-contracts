# smart-contracts
Stake DAO's smart-contracts and audits

## Testing Methodology

All smart contracts were tested using Ganache’s forked mainnet as default network, because a forked version of mainnet already has existing protocols like Curve, Opyn, etc deployed on it for our contracts to interact with, and saves time for us redeploying all of them.

## Smart Contracts Info
1. All contracts before our next release of features, are immutable.
2. Pause Control is not implemented in the current system. This was to avoid making major changes in the battle-tested smart-contracts that we re-used, which might insert some vulnerabilities.
