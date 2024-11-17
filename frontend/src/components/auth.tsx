import { execHaloCmdWeb } from "@arx-research/libhalo/api/web";
import { FC, useState } from "react";
import { toast } from "sonner";

interface Props {
  setAuth: (boolean: boolean) => void;
}

export const Auth: FC<Props> = ({ setAuth }) => {
  const [statusText, setStatusText] = useState("click on the button");
  const authenticate = async () => {
    let command = {
      name: "sign",
      keyNo: 1,
      message: "Login with your NFC card for Eth Global",
      format: "text",
    };
    let res;

    try {
      // --- request NFC command execution ---
      res = await execHaloCmdWeb(command, {
        statusCallback: (cause) => {
          if (cause === "init") {
            setStatusText(
              "Please tap the tag to the back of your smartphone and hold it...",
            );
          } else if (cause === "retry") {
            setStatusText(
              "Something went wrong, please try to tap the tag again...",
            );
          } else if (cause === "scanned") {
            setStatusText(
              "Tag scanned successfully, post-processing the result...",
            );
          } else {
            setStatusText(cause);
          }
        },
      });
      setAuth(true);
      toast("Authentication success");
      // the command has succeeded, display the result to the user
      setStatusText(JSON.stringify(res, null, 4));
    } catch (e) {
      // the command has failed, display error to the user
      setStatusText(
        "Scanning failed, click on the button again to retry. Details: " +
          String(e),
      );
      setAuth(false);
    }
  };

  return (
    <div className="flex flex-col justify-center items-center">
      <button
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        onClick={() => authenticate()}
      >
        Scan wristband
      </button>
      <p className="mt-4">{statusText}</p>
    </div>
  );
};
