import { AzureFunction, Context, HttpRequest } from '@azure/functions';

export const index: AzureFunction = async function(
  context: Context,
  req: HttpRequest
): Promise<void> {
  context.bindingData.oldFlair.forEach(element => {});
};
