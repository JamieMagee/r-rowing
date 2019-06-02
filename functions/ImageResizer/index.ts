import { AzureFunction, Context } from '@azure/functions';
import axios from 'axios';
import axiosRetry from 'axios-retry';
import sharp from 'sharp';

axiosRetry(axios, { retries: 3 });

interface OarSpotterImage {
  name: string;
  category: string;
  location?: string;
  src: string;
}

const baseUrl = 'http://www.oarspotter.com/blades/';

export const index: AzureFunction = async function(
  context: Context,
  msg: OarSpotterImage
): Promise<void> {
  const image = await sharp(await getImageBuffer(baseUrl + msg.src));
  const metadata = await image.metadata();
  if (metadata.width !== 436 && metadata.size !== 48) {
    return;
  }

  const trimmedImage = sharp(await image.trim(1).toBuffer());
  const trimmedMetadata = await trimmedImage.metadata();

  context.bindings.blob = await trimmedImage
    .extract({
      left: 351,
      top: 1,
      width: trimmedMetadata.width - 351,
      height: trimmedMetadata.height - 1
    })
    .resize(null, 14)
    .toBuffer();

  const RowKey = Buffer.from(
    msg.name + ';' + msg.category + ';' + msg.location
  ).toString('base64');

  context.bindings.table = {
    PartitionKey: 'flair',
    RowKey: RowKey,
    name: msg.name,
    category: msg.category,
    location: msg.location,
    src: msg.src
  };
};

const getImageBuffer = async (src: string): Promise<Buffer> =>
  Buffer.from(
    await (await axios.get(src, { responseType: 'arraybuffer' })).data
  );
