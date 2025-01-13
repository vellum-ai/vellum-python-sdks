import { VellumError } from "vellum-ai";
import { DocumentIndexRead, MetricDefinitionHistoryItem } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { MetricDefinitions as MetricDefinitionsClient } from "vellum-ai/api/resources/metricDefinitions/client/Client";
import { WorkflowDeployments as WorkflowDeploymentsClient } from "vellum-ai/api/resources/workflowDeployments/client/Client";

import { BaseNodeContext } from "./base";
import { GuardrailNodeContext } from "./guardrail-node";
import { InlineSubworkflowNodeContext } from "./inline-subworkflow-node";
import { TextSearchNodeContext } from "./text-search-node";

import { ApiNodeContext } from "src/context/node-context/api-node";
import { CodeExecutionContext } from "src/context/node-context/code-execution-node";
import { ConditionalNodeContext } from "src/context/node-context/conditional-node";
import { ErrorNodeContext } from "src/context/node-context/error-node";
import { FinalOutputNodeContext } from "src/context/node-context/final-output-node";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { MapNodeContext } from "src/context/node-context/map-node";
import { MergeNodeContext } from "src/context/node-context/merge-node";
import { NoteNodeContext } from "src/context/node-context/note-node";
import { PromptDeploymentNodeContext } from "src/context/node-context/prompt-deployment-node";
import { SubworkflowDeploymentNodeContext } from "src/context/node-context/subworkflow-deployment-node";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import {
  EntityNotFoundError,
  NodeDefinitionGenerationError,
} from "src/generators/errors";
import {
  InlinePromptNode,
  InlinePromptNodeData,
  LegacyPromptNodeData,
  WorkflowDataNode,
  WorkflowNodeType,
} from "src/types/vellum";
import { assertUnreachable } from "src/utils/typing";

export async function createNodeContext(
  args: BaseNodeContext.Args<WorkflowDataNode>
): Promise<BaseNodeContext<WorkflowDataNode>> {
  const nodeData = args.nodeData;
  switch (nodeData.type) {
    case WorkflowNodeType.SEARCH: {
      const searchNodeData = nodeData;

      // Grab the associated document index from api if available to always populate document_index field
      // with name instead of ID. We can only do this if the document index input is a constant value.
      let documentIndex: DocumentIndexRead | null = null;
      const inputValue = searchNodeData.inputs.find(
        (input) => input.id === searchNodeData.data.documentIndexNodeInputId
      )?.value;

      const rule = inputValue?.rules?.[0];
      if (rule?.type === "CONSTANT_VALUE") {
        if (rule.data.value?.toString()) {
          try {
            documentIndex = await new DocumentIndexesClient({
              apiKey: args.workflowContext.vellumApiKey,
            }).retrieve(rule.data.value?.toString());
          } catch (e) {
            if (e instanceof VellumError && e.statusCode === 404) {
              args.workflowContext.addError(
                new EntityNotFoundError(
                  `Document Index "${rule.data.value?.toString()}" not found.`
                )
              );
            } else {
              throw e;
            }
          }
        }
      }

      return new TextSearchNodeContext({
        ...args,
        documentIndex,
        nodeData: searchNodeData,
      });
    }
    case WorkflowNodeType.SUBWORKFLOW: {
      const subworkflowNodeData = nodeData;

      const subworkflowVariant = subworkflowNodeData.data.variant;
      switch (subworkflowVariant) {
        case "INLINE": {
          return new InlineSubworkflowNodeContext({
            ...args,
            nodeData: subworkflowNodeData,
          });
        }
        case "DEPLOYMENT": {
          const { releaseTag, workflowDeploymentId } = subworkflowNodeData.data;
          const workflowDeploymentHistoryItem =
            await new WorkflowDeploymentsClient({
              apiKey: args.workflowContext.vellumApiKey,
            }).workflowDeploymentHistoryItemRetrieve(
              releaseTag,
              workflowDeploymentId
            );

          return new SubworkflowDeploymentNodeContext({
            ...args,
            nodeData: subworkflowNodeData,
            workflowDeploymentHistoryItem,
          });
        }
        default: {
          assertUnreachable(subworkflowVariant);
        }
      }
      break;
    }
    case WorkflowNodeType.MAP: {
      const mapNodeData = nodeData;
      const variant = mapNodeData.data.variant;
      if (variant === "INLINE") {
        return new MapNodeContext({
          ...args,
          nodeData: mapNodeData,
        });
      } else {
        throw new NodeDefinitionGenerationError(
          `MapNode only supports INLINE variant. Received: ${variant}`
        );
      }
    }
    case WorkflowNodeType.METRIC: {
      const guardrailNodeData = nodeData;
      let metricDefinitionsHistoryItem:
        | MetricDefinitionHistoryItem
        | undefined = undefined;

      try {
        metricDefinitionsHistoryItem = await new MetricDefinitionsClient({
          apiKey: args.workflowContext.vellumApiKey,
        }).metricDefinitionHistoryItemRetrieve(
          guardrailNodeData.data.releaseTag,
          guardrailNodeData.data.metricDefinitionId
        );
      } catch (e) {
        if (e instanceof VellumError && e.statusCode === 404) {
          args.workflowContext.addError(
            new EntityNotFoundError(
              `Metric Definition "${guardrailNodeData.data.metricDefinitionId} ${guardrailNodeData.data.releaseTag}" not found.`
            )
          );
        } else {
          throw e;
        }
      }

      return new GuardrailNodeContext({
        ...args,
        nodeData: guardrailNodeData,
        metricDefinitionsHistoryItem,
      });
    }
    case WorkflowNodeType.CODE_EXECUTION: {
      const codeExecutionNodeData = nodeData;
      return new CodeExecutionContext({
        ...args,
        nodeData: codeExecutionNodeData,
      });
    }
    case WorkflowNodeType.PROMPT: {
      const promptNodeData = nodeData;

      const promptVariant = promptNodeData.data.variant;
      switch (promptVariant) {
        case "INLINE": {
          return new InlinePromptNodeContext({
            ...args,
            nodeData: promptNodeData as InlinePromptNode,
          });
        }
        case "LEGACY": {
          // In the legacy case, we simply convert from LEGACY to INLINE on the fly.
          const legacyNodeData: LegacyPromptNodeData = promptNodeData.data;

          const promptVersionData =
            legacyNodeData.sandboxRoutingConfig.promptVersionData;
          if (!promptVersionData) {
            throw new NodeDefinitionGenerationError(
              `Prompt version data not found`
            );
          }

          // Dynamically fetch the ML Model's name via API
          const mlModelName = await args.workflowContext.getMLModelNameById(
            promptVersionData.mlModelToWorkspaceId
          );

          const inlinePromptNodeData: InlinePromptNodeData = {
            ...legacyNodeData,
            variant: "INLINE",
            mlModelName,
            execConfig: promptVersionData.execConfig,
          };

          return new InlinePromptNodeContext({
            ...args,
            nodeData: { ...promptNodeData, data: inlinePromptNodeData },
          });
        }
        case "DEPLOYMENT": {
          return new PromptDeploymentNodeContext({
            ...args,
            nodeData: promptNodeData,
          });
        }
        default: {
          assertUnreachable(promptVariant);
        }
      }
      break;
    }
    case WorkflowNodeType.TEMPLATING: {
      const templatingNodeData = nodeData;
      return new TemplatingNodeContext({
        ...args,
        nodeData: templatingNodeData,
      });
    }
    case WorkflowNodeType.CONDITIONAL: {
      const conditionalNodeData = nodeData;
      return new ConditionalNodeContext({
        ...args,
        nodeData: conditionalNodeData,
      });
    }
    case WorkflowNodeType.API: {
      const apiNodeData = nodeData;
      return new ApiNodeContext({
        ...args,
        nodeData: apiNodeData,
      });
    }
    case WorkflowNodeType.TERMINAL: {
      const terminalNodeData = nodeData;
      return new FinalOutputNodeContext({
        ...args,
        nodeData: terminalNodeData,
      });
    }
    case WorkflowNodeType.MERGE: {
      const mergeNodeData = nodeData;
      return new MergeNodeContext({
        ...args,
        nodeData: mergeNodeData,
      });
    }
    case WorkflowNodeType.ERROR: {
      const errorNodeData = nodeData;
      return new ErrorNodeContext({
        ...args,
        nodeData: errorNodeData,
      });
    }
    case WorkflowNodeType.NOTE: {
      const noteNodeData = nodeData;
      return new NoteNodeContext({
        ...args,
        nodeData: noteNodeData,
      });
    }
    case WorkflowNodeType.GENERIC: {
      const genericNodeData = nodeData;
      return new GenericNodeContext({
        ...args,
        nodeData: genericNodeData,
      });
    }
    default:
      throw new NodeDefinitionGenerationError(
        `Unsupported node type: ${args.nodeData.type}`
      );
  }
}
