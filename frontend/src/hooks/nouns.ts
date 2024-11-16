import { UseMutationResult, useQuery, UseQueryResult, } from "@tanstack/react-query";
import { nounsApi } from "../api";

export const useNouns = (): UseQueryResult<string, Error> => {
  return useQuery<string, Error>({
    queryKey: ["nouns"],

    queryFn: nounsApi.getNouns,
  });
};