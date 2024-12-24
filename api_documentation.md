# WhatsApp Integration API Documentation

## Overview

This documentation provides details about the WhatsApp Integration API, allowing you to send messages and handle webhooks.

---

## API Details

### General Information

- **API Version**: v1
- **Contact Email**: [wankhedeashok9822@gmail.com](wankhedeashok9822@gmail.com)

### Host and Schemes

- **Host**: `172.20.1.140:8002`
- **Schemes**: `http`
- **Base Path**: `/`

### Supported Content Types

- **Consumes**: `application/json`
- **Produces**: `application/json`



## API Endpoints

### 1. Send Message Endpoint

#### **POST /**

**Description**: API to send a message.

#### Parameters:

| Name       | In   | Type   | Required | Description                              |
|------------|------|--------|----------|------------------------------------------|
| `data`     | Body | Object | Yes      | Contains `receiver` and `message`.      |

- **Request Body Schema**:
  ```json
  {
    "receiver": ["+1234567890", "+0987654321"],
    "message": "Your message content here."
  }
  ```

- **Response Codes**:
  | Code | Description                     |
  |------|---------------------------------|
  | 200  | Message sent successfully       |
  | 400  | Receiver and message are required |

#### Example Request
```json
{
  "receiver": ["+1234567890"],
  "message": "Hello, this is a test message."
}
```

#### Example Response (Success)
```json
{
  "status": "Message sent successfully"
}
```

---

### 2. WhatsApp Webhook Endpoint

#### **GET /whatsapp_webhook**

**Description**: Verifies the webhook.

#### Parameters:

| Name                 | In    | Type   | Required | Description                        |
|----------------------|-------|--------|----------|------------------------------------|
| `hub.verify_token`   | Query | String | No       | Token to verify the webhook        |
| `hub.challenge`      | Query | String | No       | Challenge token to respond with    |

- **Response Codes**:
  | Code | Description              |
  |------|--------------------------|
  | 200  | Challenge token response |
  | 403  | Invalid token            |
  | 500  | Unexpected error         |

---

#### **POST /whatsapp_webhook**

**Description**: Handles incoming webhook payloads.

#### Parameters:

| Name       | In   | Type   | Required | Description                           |
|------------|------|--------|----------|---------------------------------------|
| `data`     | Body | Object | Yes      | Payload containing webhook entries.  |

- **Request Body Schema**:
  ```json
  {
    "entry": [
      {
        //recevied messages
      }
    ]
  }
  ```

- **Response Codes**:
  | Code | Description                                 |
  |------|---------------------------------------------|
  | 200  | Success response                           |
  | 400  | Missing entry data                         |
  | 500  | Error processing webhook or saving message |



#### Example Response (Success)
```json
{
  "status": "Success"
}
```


