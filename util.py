import aiohttp


async def get_new_emotes(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def get_new_emotes_7tv(url):
    request_body = {
        "query": "query($query: String!,$page: Int,$pageSize: Int,$globalState: String,$sortBy: String,$sortOrder: Int,$channel: String,$submitted_by: String,$filter: EmoteFilter) {search_emotes(query: $query,limit: $pageSize,page: $page,pageSize: $pageSize,globalState: $globalState,sortBy: $sortBy,sortOrder: $sortOrder,channel: $channel,submitted_by: $submitted_by,filter: $filter) {id,visibility,owner {id,display_name,role {id,name,color},banned}name,tags}}",
        "variables": {
            "channel": None,
            "globalState": None,
            "limit": 22,
            "page": 1,
            "pageSize": 22,
            "query": "",
            "sortBy": "age",
            "sortOrder": 0,
            "submitted_by": None,
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=request_body) as response:
            return await response.json()