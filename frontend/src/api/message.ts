import { backendUrls } from "../constants";
import { Message, messageSchema } from "../types/messages";
import client, { validateResponse } from "./client";

export const messageApi = {
  postMessage: async (message: string): Promise<Message> => {
    const response = await client.post(backendUrls.postMessage, {
      message,
    });
    return validateResponse(messageSchema, response.data);
  },
};
