const hre = require("hardhat");

async function main() {
    const VeritasProofAnchor = await hre.ethers.getContractFactory("VeritasProofAnchor");

    const contract = await VeritasProofAnchor.deploy();

    await contract.waitForDeployment();

    console.log("================================");
    console.log("VeritasProofAnchor deployed at:");
    console.log(await contract.getAddress());
    console.log("================================");
}

main().catch((err) => {
    console.error(err);
    process.exitCode = 1;
});