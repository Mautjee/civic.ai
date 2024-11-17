import { UseMutationResult, useMutation } from "@tanstack/react-query";
import { messageApi } from "../api";
import { Message } from "@/types/messages";

export const useMessage = (): UseMutationResult<
  Message,
  Error,
  string,
  unknown
> => {
  return useMutation<Message, Error, string>({
    mutationKey: ["messagePost"],
    mutationFn: (message: string) => messageApi.postMessage(message),
  });
};
