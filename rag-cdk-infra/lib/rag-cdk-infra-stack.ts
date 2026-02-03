import * as cdk from 'aws-cdk-lib/core';
import { Construct } from 'constructs';

import {
  DockerImageFunction,
  DockerImageCode,
  FunctionUrlAuthType,
  Architecture,
} from "aws-cdk-lib/aws-lambda";
import { ManagedPolicy } from 'aws-cdk-lib/aws-iam';
import { platform } from 'os';
import { AttributeType, BillingMode, Table } from 'aws-cdk-lib/aws-dynamodb';

export class RagCdkInfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Creating a DDB table to store query data and results
    const ragQueryTable = new Table(this, "RagQueryTable", {
      partitionKey: { name: "query_id", type: AttributeType.STRING},
      billingMode: BillingMode.PAY_PER_REQUEST,
    });

    // Lambda function (image) to handle the worker logic (run RAG/AI model).
    const workerImageCode = DockerImageCode.fromImageAsset("../image", {
      cmd: ["app_work_handler.handler"],
      buildArgs: {
        platform: "linux/amd64",
      },
    });
    const workerFunction = new DockerImageFunction(this, "RagWorkerFunction", {
      code: workerImageCode,
      memorySize: 512,
      timeout: cdk.Duration.seconds(60),
      architecture: Architecture.X86_64,
      environment: {
        TABLE_NAME: ragQueryTable.tableName,
        OPENAI_API_KEY: process.env.OPENAI_API_KEY!,
      },
    });


    // Function to handle API requests, uses same base image, but different handler.
    const apiImageCode = DockerImageCode.fromImageAsset("../image", {
      cmd: ["app_api_handler.handler"],
      buildArgs: {
        platform: "linux/amd64"
      },
    });

    // Creating a function using the docker image code, creates docker container specs.
    const apiFunction = new DockerImageFunction(this, "ApiFunc", {
      code: apiImageCode,
      memorySize: 256,
      timeout: cdk.Duration.seconds(30),
      architecture: Architecture.X86_64,
      environment: {
        TABLE_NAME: ragQueryTable.tableName,
        OPENAI_API_KEY: process.env.OPENAI_API_KEY!,
        WORKER_LAMBDA_NAME: workerFunction.functionName,
      },
    });

    // Public URL for API function.
    const functionUrl = apiFunction.addFunctionUrl({
      authType: FunctionUrlAuthType.NONE,
    });

    // Grant permissions for all resources to work together.
    ragQueryTable.grantReadWriteData(workerFunction);
    ragQueryTable.grantReadWriteData(apiFunction);
    workerFunction.grantInvoke(apiFunction);

    // Output the URL for API function. 
    new cdk.CfnOutput(this, "FunctionUrl", {
      value: functionUrl.url,
    });
  }
}
