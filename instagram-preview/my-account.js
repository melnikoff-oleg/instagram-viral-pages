// Your draft account, shown on me.html and in the studio's Packaging card. Hand-edited (by you or Claude), never regenerated.
// The handle is set in one place below. Posts are newest first; reel-N numbering matches reels/.
// Posts: kind "image" | "carousel" | "reel"; reels need "video" (mp4 in assets/mine/), "audio" and "taken_at" (unix seconds).
// "thread" is the list of comments shown under the caption; a comment can carry "replies" (same shape); "self: true" is the account itself.
var HANDLE = 'yourhandle';

window.IG_PROFILE = {
  username: HANDLE,
  verified: false,
  note: '',
  posts: '0', followers: '0', following: '0',
  category: 'Digital creator',
  bio: '',
  link: null,
  threads: HANDLE,
  avatar: 'assets/placeholder-avatar.png',
  storyRing: false,
  viewerAvatar: 'assets/placeholder-avatar.png'
};

window.IG_POSTS = [
  // {
  //   file: 'assets/mine/reel-1.jpg',
  //   href: '/' + HANDLE + '/reel/1/',
  //   kind: 'reel',
  //   pinned: true,
  //   label: 'AI content',
  //   caption: 'Subject × Place\n\n#one #two #three',
  //   video: 'assets/mine/reel-1.mp4',
  //   audio: HANDLE + ' • Original audio',
  //   likes: 0, comments: 0, reposts: 0,
  //   taken_at: 1793178000,
  //   thread: [
  //     { user: 'someone', text: 'wait what film is this', ago: '2h', likes: 12,
  //       replies: [{ user: HANDLE, self: true, text: 'one that was never made 🎬', ago: '2h', likes: 30 }] }
  //   ]
  // }
];
