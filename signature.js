import crypto from "crypto";

class SignatureGenerator {
  constructor(secretKey = "W_ak^moHpMla") {
    this.secretKey = secretKey;
  }

  /**
   * Generates a signature for the given client ID
   * @param {string} clientId - The client ID
   * @returns {string} The generated signature
   */
  generateSignature(clientId) {
    const timestamp = this.getTimestamp();
    const toHash = `${timestamp},${clientId}`;
    const hash = this.md5Hash(toHash);
    return `${hash},${timestamp}`;
  }

  /**
   * Generates s and t data for the given input data
   * @param {Object} data - The data object containing properties like spuId
   * @returns {Object} Object containing s (hash) and t (timestamp)
   */
  generateSData(data) {
    const timestamp = this.getTimestamp();
    // Create JSON string with proper escaping for specific properties
    const jsonData = "{\"spuId\":\"" + data.spuId + "\"}";
    const toHash = `${jsonData}${this.secretKey}`;
    const hash = this.md5Hash(toHash + timestamp);
    
    return {
      s: hash,
      t: timestamp,
    };
  }

  /**
   * Creates an MD5 hash of the input string
   * @param {string} input - The string to hash
   * @returns {string} The MD5 hash as a hex string
   */
  md5Hash(input) {
    return crypto.createHash("md5").update(input).digest("hex");
  }

  /**
   * Gets the current Unix timestamp in seconds
   * @returns {number} The current timestamp
   */
  getTimestamp() {
    return Math.floor(Date.now() / 1000);
  }
}

export default SignatureGenerator;