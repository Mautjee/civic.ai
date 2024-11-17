import { FC, useEffect, useState } from "react";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";
import { toast } from "sonner";
import { useMessage } from "@/hooks/messages";
import Noun from "./noun";

export const Submit: FC = () => {
  const [message, setMessage] = useState("");
  const [statusText, setStatusText] = useState("please speak your thoughts");
  const { data, error, mutate } = useMessage();

  useEffect(() => {
    if (error) {
      setStatusText(error.message);
    } else if (data) {
      setStatusText(data.message);
    }
  }, [data, error]);

  const onSubmit = () => {
    mutate(message);
    toast("Message sent");
  };

  return (
    <div className="w-full h-full flex flex-col justify-center items-center gap-4">
      <Noun />
      <h1 className="text-3xl font-bold">Spaeak your thoughts</h1>
      <Textarea onChange={(e) => setMessage(e.target.value)} />
      <Button onClick={onSubmit}>Submit</Button>
      <p>{statusText}</p>
    </div>
  );
};
