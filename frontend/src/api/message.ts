import { backendUrls } from "../constants";
import { MessagePost, messagePost } from "../types/messages";
import client, { validateResponse } from "./client";

export const messageApi = {
  postMessage: async (): Promise<MessagePost> => {
    const response = await client.post(backendUrls.postMessage);
    return validateResponse(messagePost, response.data);
  },
};
