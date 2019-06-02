import Snoowrap = require('snoowrap');

const r = new Snoowrap({
  userAgent: 'RowingFlairBot by Jammie1',
  clientId: process.env.CLIENT_ID,
  clientSecret: process.env.CLIENT_SECRET,
  refreshToken: process.env.REFRESH_TOKEN
});

const tableRegex = /\*\*Upcoming Races\*\*\s\S/;

export const setSidebar = async (content: string): Promise<void> => {
  const sub = r.getSubreddit('jammie1');
  const settings = await sub.getSettings();
  settings.description = settings.description.replace(tableRegex, content);
  sub.editSettings(settings);
};
