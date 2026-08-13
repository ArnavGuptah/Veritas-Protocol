require("@nomicfoundation/hardhat-toolbox");

require("dotenv").config({
  path: "../backend/.env" ,
});

console.log(process.cwd());
console.log("RPC =", process.env.SEPOLIA_RPC_URL);
console.log("KEY =", process.env.PRIVATE_KEY?.slice(0, 10));

module.exports = {
  solidity: "0.8.20",

  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: process.env.PRIVATE_KEY
        ? [process.env.PRIVATE_KEY]
        : [],
    },
  },
};