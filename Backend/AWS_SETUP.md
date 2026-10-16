# AWS Backend Setup

## Region
- AWS Region: ap-south-1 (Asia Pacific - Mumbai)

## Amazon Cognito
- User Pool ID: ap-south-1_BQoeXub6X
- Frontend authentication uses AWS Amplify.
- Configure the frontend app client as a public SPA with authorization code flow and PKCE.
- Configure callback and sign-out URLs for the deployed frontend.
- Do not use a client secret in browser code.

## Amazon DynamoDB
- Table: Assessments
- Partition key: assessmentId (String)
- Billing mode: PAY_PER_REQUEST
- The backend uses AWS SDK DocumentClient to read and write assessments.

## AWS Lambda
- Source folders:
  - lambda/
  - lambda-deploy/
  - report-lambda/
- Review each handler and configure its runtime, handler entry point, environment variables, and execution role before deployment.
- Configure triggers or API Gateway integration only where required by the application.

## AWS IAM
- Use least-privilege execution roles for Lambda.
- Grant only the DynamoDB, Bedrock, S3, and SNS actions required by each function.
- Review bedrock-policy.json before attaching it to any role.
- Never commit access keys, secret keys, passwords, tokens, or .env files.

## Local Backend
1. Install Node.js dependencies with npm install inside Backend/.
2. Configure local environment variables in an untracked .env file.
3. Authenticate with AWS using an approved AWS CLI login or credential provider.
4. Start the API using the script defined in package.json.
5. Test GET /api/health before testing authenticated assessment endpoints.

## Deployment Checklist
- Verify IAM permissions and resource ARNs.
- Confirm all resources use the intended AWS region.
- Verify Cognito token validation.
- Test DynamoDB access and Lambda handlers.
- Confirm Bedrock model access and required S3/SNS permissions.
- Never store credentials or real user assessment data in this repository.
