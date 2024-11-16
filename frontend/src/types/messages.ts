import { z } from "zod";

export const messageSchema = z.object({
  message: z.string(),
});

export type Message = z.infer<typeof messageSchema>;
