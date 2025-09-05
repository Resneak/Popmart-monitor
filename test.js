import SignatureGenerator from './signature.js';

// Create an instance of the SignatureGenerator class
const signatureGen = new SignatureGenerator();

// Generate signature and s/t data
const clientId = "nw3b089qrgw9m7b7i";
const signature = signatureGen.generateSignature(clientId);

const { s, t } = signatureGen.generateSData({
    spuId: "878",
});

// Send the request
fetch(`https://prod-global-api.popmart.com/shop/v1/shop/productDetails?spuId=878&s=${s}&t=${t}`, {
    "headers": {
      "accept": "application/json, text/plain, */*",
      "accept-language": "en-US,en;q=0.9",
      "cache-control": "no-cache",
      "clientkey": "nw3b089qrgw9m7b7i",
      "country": "US",
      "language": "en",
      "pragma": "no-cache",
      "priority": "u=1, i",
      "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": "\"macOS\"",
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "same-site",
      "td-session-key": "", 
      "td-session-path": "/shop/v1/shop/productDetails",
      "td-session-query": "",
      "tz": "America/Chicago",
      "x-client-country": "US",
      "x-client-namespace": "america",
      "x-device-os-type": "web",
      "x-project-id": "naus",
      "x-sign": signature,
    },
    "referrer": "https://www.popmart.com/",
    "referrerPolicy": "strict-origin-when-cross-origin",
    "body": null,
    "method": "GET",
    "mode": "cors",
    "credentials": "omit"
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));