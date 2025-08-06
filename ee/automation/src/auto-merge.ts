import { Octokit } from '@octokit/rest';
import { getGithubToken } from './auth.js';
import * as dotenv from 'dotenv';

dotenv.config();

const SDK_REPO = "vellum-python-sdks";
const PR_NUMBER = parseInt(process.env.PR_NUMBER || '0');
const HEAD_SHA = process.env.HEAD_SHA;

const POLL_INTERVAL = 30000; // 30 seconds
const MAX_WAIT_TIME = 30 * 60 * 1000; // 30 minutes

interface CheckRun {
  status: string;
  conclusion: string | null;
  name: string;
}

const main = async () => {
  if (!SDK_REPO || !PR_NUMBER || !HEAD_SHA) {
    throw new Error('Missing required environment variables: FERN_SDK_REPO, PR_NUMBER, HEAD_SHA');
  }

  console.log(`Starting auto-merge process for PR #${PR_NUMBER} in ${SDK_REPO}`);
  console.log(`Head SHA: ${HEAD_SHA}`);

  const auth = await getGithubToken();
  const octokit = new Octokit({ auth });

  const owner = "vellum-ai";
  const repo = SDK_REPO;

  const { data: pr } = await octokit.rest.pulls.get({
    owner,
    repo,
    pull_number: PR_NUMBER,
  });

  if (!pr.labels.some(label => label.name === 'release')) {
    console.log('PR does not have release label, skipping auto-merge');
    return;
  }

  if (pr.state !== 'open') {
    console.log(`PR is ${pr.state}, skipping auto-merge`);
    return;
  }

  console.log(`PR #${PR_NUMBER} is open and has release label, waiting for checks...`);

  const startTime = Date.now();
  
  while (Date.now() - startTime < MAX_WAIT_TIME) {
    try {
      const { data: checkRuns } = await octokit.rest.checks.listForRef({
        owner,
        repo,
        ref: HEAD_SHA,
      });

      console.log(`Found ${checkRuns.total_count} check runs`);

      if (checkRuns.total_count === 0) {
        console.log('No check runs found, waiting...');
        await sleep(POLL_INTERVAL);
        continue;
      }

      const checks: CheckRun[] = checkRuns.check_runs.map(run => ({
        status: run.status,
        conclusion: run.conclusion,
        name: run.name,
      }));

      const pendingChecks = checks.filter(check => check.status !== 'completed');
      if (pendingChecks.length > 0) {
        console.log(`Waiting for ${pendingChecks.length} checks to complete:`, 
          pendingChecks.map(c => c.name).join(', '));
        await sleep(POLL_INTERVAL);
        continue;
      }

      const failedChecks = checks.filter(check => 
        check.conclusion !== 'success' && check.conclusion !== 'neutral' && check.conclusion !== 'skipped'
      );

      if (failedChecks.length > 0) {
        console.log('Some checks failed, cannot auto-merge:');
        failedChecks.forEach(check => {
          console.log(`  - ${check.name}: ${check.conclusion}`);
        });
        return;
      }

      console.log('All checks passed! Attempting to merge PR...');

      try {
        await octokit.rest.pulls.merge({
          owner,
          repo,
          pull_number: PR_NUMBER,
          merge_method: 'squash',
          commit_title: `${pr.title} (#${PR_NUMBER})`,
        });

        console.log(`Successfully auto-merged PR #${PR_NUMBER}`);
        return;
      } catch (mergeError: any) {
        if (mergeError.status === 405) {
          console.log('PR cannot be merged (may have conflicts or branch protection rules)');
        } else {
          console.error('Error merging PR:', mergeError.message);
        }
        return;
      }

    } catch (error: any) {
      console.error('Error checking status:', error.message);
      await sleep(POLL_INTERVAL);
    }
  }

  console.log('Timeout reached, stopping auto-merge process');
};

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

main().catch(console.error);
