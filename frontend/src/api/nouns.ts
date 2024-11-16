import { Nouns_API } from "../constants";
import client from "./client";

export const nounsApi = {
  getNouns: async (): Promise<string> => {
    const response = await client.get(Nouns_API);
    return response;
  },
};
