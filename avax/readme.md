## Deployment steps

```sh
npx hardhat deploy --network avax --export deployment.json
npx hardhat sourcify --network avax
npx hardhat configure-aave --network avax
```

Multirewards contract are taken from Curve 
[MultiRewards](https://github.com/curvefi/multi-rewards/blob/master/contracts/MultiRewards.sol)
And differences can be inspected on the [Diffchecker](https://www.diffchecker.com/JnKF55JE)

