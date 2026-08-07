// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Veritas Proof Anchor
/// @author Veritas Protocol
/// @notice Stores ONLY proof metadata on-chain.
/// @dev
/// The blockchain is used only to prove integrity and provenance.
/// AI reasoning, retrieved evidence, embeddings, documents, and Proof Objects
/// remain completely off-chain.
///
/// Recommended deployment:
/// - Polygon Amoy Testnet
/// - Base Sepolia Testnet

contract VeritasProofAnchor {

    // ------------------------------------------------------------------------
    // Errors
    // ------------------------------------------------------------------------

    error ProofAlreadyExists(string proofId);
    error ProofNotFound(string proofId);

    // ------------------------------------------------------------------------
    // Data Model
    // ------------------------------------------------------------------------

    struct ProofRecord {
        bytes32 rootHash;          // Final Proof Object hash
        uint256 timestamp;         // Block timestamp
        bytes verifierSignature;   // Cryptographic verifier signature
        address submitter;         // Wallet that anchored the proof
    }

    mapping(string => ProofRecord) private proofs;
    string[] private proofIds;

    // ------------------------------------------------------------------------
    // Events
    // ------------------------------------------------------------------------

    event ProofAnchored(
        string indexed proofId,
        bytes32 indexed rootHash,
        address indexed submitter,
        uint256 timestamp
    );

    // ------------------------------------------------------------------------
    // Write Functions
    // ------------------------------------------------------------------------

    function storeProof(
        string calldata proofId,
        bytes32 rootHash,
        bytes calldata verifierSignature
    ) external {

        if (proofs[proofId].timestamp != 0) {
            revert ProofAlreadyExists(proofId);
        }

        proofs[proofId] = ProofRecord({
            rootHash: rootHash,
            timestamp: block.timestamp,
            verifierSignature: verifierSignature,
            submitter: msg.sender
        });

        proofIds.push(proofId);

        emit ProofAnchored(
            proofId,
            rootHash,
            msg.sender,
            block.timestamp
        );
    }

    // ------------------------------------------------------------------------
    // Read Functions
    // ------------------------------------------------------------------------

    function verifyProof(
        string calldata proofId,
        bytes32 claimedRootHash
    )
        external
        view
        returns (bool)
    {
        return proofs[proofId].rootHash == claimedRootHash;
    }

    function getProof(
        string calldata proofId
    )
        external
        view
        returns (
            bytes32 rootHash,
            uint256 timestamp,
            bytes memory verifierSignature,
            address submitter
        )
    {
        ProofRecord storage proof = proofs[proofId];

        if (proof.timestamp == 0) {
            revert ProofNotFound(proofId);
        }

        return (
            proof.rootHash,
            proof.timestamp,
            proof.verifierSignature,
            proof.submitter
        );
    }

    function totalProofs()
        external
        view
        returns (uint256)
    {
        return proofIds.length;
    }

    function proofExists(
        string calldata proofId
    )
        external
        view
        returns (bool)
    {
        return proofs[proofId].timestamp != 0;
    }
}