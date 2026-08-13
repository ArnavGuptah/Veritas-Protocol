// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Veritas Proof Anchor
/// @author Veritas Protocol
/// @notice Stores proof metadata on-chain only.
contract VeritasProofAnchor {

    // ------------------------------------------------------------------------
    // Errors
    // ------------------------------------------------------------------------

    error ProofAlreadyExists(string proofId);
    error ProofNotFound(string proofId);

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
    // Data Model
    // ------------------------------------------------------------------------

    struct ProofRecord {
        bytes32 rootHash;
        uint256 timestamp;
        bytes verifierSignature;
        address submitter;
    }

    mapping(string => ProofRecord) private proofs;

    uint256 public totalProofs;

    // ------------------------------------------------------------------------
    // Store Proof
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

        totalProofs++;

        emit ProofAnchored(
            proofId,
            rootHash,
            msg.sender,
            block.timestamp
        );
    }

    // ------------------------------------------------------------------------
    // Verify
    // ------------------------------------------------------------------------

    function verifyProof(
        string calldata proofId,
        bytes32 claimedRootHash
    ) external view returns (bool) {

        ProofRecord storage proof = proofs[proofId];

        if (proof.timestamp == 0) {
            return false;
        }

        return proof.rootHash == claimedRootHash;
    }

    // ------------------------------------------------------------------------
    // Exists
    // ------------------------------------------------------------------------

    function proofExists(
        string calldata proofId
    ) external view returns (bool) {

        return proofs[proofId].timestamp != 0;
    }

    // ------------------------------------------------------------------------
    // Read
    // ------------------------------------------------------------------------

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
}