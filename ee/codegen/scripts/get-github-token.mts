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

  const auth = createAppAuth({
    appId,
    privateKey,
    installationId,
  });

  const { token } = await auth({ type: "installation" });
  return token;
};
