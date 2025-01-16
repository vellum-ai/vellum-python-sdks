import { createAppAuth } from "@octokit/auth-app";

export const getGithubToken = async () => {
  const appId = process.env.VELLUM_AUTOMATION_APP_ID;
  const privateKey = process.env.VELLUM_AUTOMATION_PRIVATE_KEY;
  const installationId = process.env.VELLUM_AUTOMATION_INSTALLATION_ID;

  if (!appId || !privateKey || !installationId) {
    throw new Error(
      "VELLUM_AUTOMATION_APP_ID, VELLUM_AUTOMATION_PRIVATE_KEY, and VELLUM_AUTOMATION_INSTALLATION_ID must be set"
    );
  }

  if (
    !privateKey.startsWith("-----BEGIN RSA PRIVATE KEY-----") ||
    !privateKey.endsWith("-----END RSA PRIVATE KEY-----")
  ) {
    throw new Error(
      `VELLUM_AUTOMATION_PRIVATE_KEY is an invalid. Please use the valid private key from \
1password and store in your .env file. Also be sure to \`unset\` any VELLUM_AUTOMATION_* \
env vars from your shell before running the script again.`
    );
  }

  const auth = createAppAuth({
    appId,
    privateKey,
    installationId,
  });

  const { token } = await auth({ type: "installation" });
  return token;
};
