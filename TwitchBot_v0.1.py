import discord,os,asyncio,requests,json
from discord.ext import commands

# token set
token_path = os.path.dirname(os.path.abspath( __file__ ) )+"/token.txt"
t = open(token_path, "r", encoding="utf-8")
token = t.read().split()[0]

# info set
client = commands.Bot(command_prefix='/')


@client.event
async def on_ready():
    state = discord.Game("트수 일")
    await client.change_presence(status=discord.Status.online, activity=state)

#pass_context=True ?

@client.command()
async def hi(m):
    await m.send("[+] Test command")


@client.command()
async def info(m):
    embed = discord.Embed(title = f"", description = f"", color = 0x5882FA)
    embed.set_author(name = "트위치 알람용", url = "", icon_url = "https://cdn.discordapp.com/avatars/752833391677931570/e0fc9333c25ee15dc6f91eecf0fb4cc3.png")
    embed.add_field(name = "> 기본", value = "/info : 봇 정보", inline = False)
    embed.add_field(name = "\n> 스트리머 알림", value = "/streamer(s) : 스트리머 현황 조회 \n/alarm(a) state (-d): 알림 설정 현황\n/a (스트리머) [add/del] : 스트리머 추가/삭제\n/a (스트리머) [on/off] : 방송 알림 ON/OFF", inline = False)
    embed.add_field(name = "\n> 키워드 알림", value = "/keyword(k) show all : 서버 설정 단어 \n /k state : 키워드 설정 현황 \n/k (단어) [on/off] : 키워드 알림 ON/OFF ", inline = False)
    await m.send(embed=embed)


@client.command()
async def streamer(m, s_id):
    embed = get_StreamState(s_id)
    await m.send(embed=embed)


@client.command()
async def s(m,s_id):
    await streamer(m,s_id)



def get_StreamToken(s_id):
    secet_id = 'Your SECET_ID'
    client_id = 'Your CLINT_ID'
    
    rq = requests.post("https://id.twitch.tv/oauth2/token?client_id=" + client_id + "&client_secret="+ secet_id +"&grant_type=client_credentials")   
    bear_id = rq.text.split('"')[3]

    url = f"https://api.twitch.tv/helix/search/channels?query=" + s_id
    header = {'Authorization': 'Bearer '+ bear_id,
              'Client-ID': client_id } 
    r = requests.get(url = url, headers = header)
    s_state = r.json()

    url = f"https://api.twitch.tv/helix/channels?broadcaster_id="+ s_state['data'][0]['id'] 
    header = {'Authorization': 'Bearer '+ bear_id,
              'Client-ID': client_id } 
    r = requests.get(url = url, headers = header)
    g_state = r.json()

    return r, s_state, g_state

def get_StreamState(s_id):
    r, s_state, g_state = get_StreamToken(s_id)

    if r.status_code == 200:
        if s_state['data'][0]['is_live'] == True:
            embed = discord.Embed(title = f"", description = f"", color = 0x5882FA)
            embed.set_author(name = g_state['data'][0]['broadcaster_name'] + " (ONLINE)", url = "", icon_url = s_state['data'][0]['thumbnail_url'])
            embed.add_field(name = f"게임 : " + g_state['data'][0]['game_name'], value = f"Title : "+ g_state['data'][0]['title']+"\nI   D : "+s_state['data'][0]['display_name'], inline = False)
            return embed
        else : 
            embed = discord.Embed(title = f"", description = f"", color = 0x5882FA)
            embed.set_author(name = g_state['data'][0]['broadcaster_name'] + " (OFFLINE)", url = "", icon_url = s_state['data'][0]['thumbnail_url'])
            return embed
    else:
        print("[+] Not 200 code")



@client.command()
async def alarm(m, arg1, arg2):
    # arg2 setting
    op = ''
    if arg2 == '-d' or arg2 == '-detail':
        op = arg2
        arg2 = m.author.id
    elif arg2[:2] == '<@':
        arg2 = arg2[2:-1]
    print(str(arg2))
    srv_name = str(m.message.guild)
    user_name = str(m.message.author)
    user_nick = user_name[:-5]
    print(str(srv_name)+'\n'+str(user_name)+'\n'+'test nick >'+user_nick)
    print('test id >'+str(arg2))
    
    userfile = os.path.join(srv_name,user_nick)
    
    while True:
        if os.path.isdir(srv_name):
            #print(user_name+"/////"+user_nick)

            if os.path.exists(userfile+".txt"):
                f = open(userfile+'.txt','r')
                lines = f.readlines()

                if arg1 == 'state' or arg1 == 's':
                    user_id = arg2

                    url = f'https://discordapp.com/api/users/'+ str(user_id)
                    header = {'Authorization': 'Bot '+ token}
                    r = requests.get(url = url, headers = header)
                    u_state = r.json()
                    target_nick = str(u_state['username'])
                     
                    print('[+]'+user_nick+'님이 '+target_nick+'님의 정보를 조회하였습니다.') 
                    
                    #파일 재설정
                    schfile = os.path.join(srv_name,target_nick)
                    f = open(schfile+'.txt','r')
                    lines = f.readlines()

                    user_on = user_off = ''

                    if op =='-detail' or op =='-d':
                        for line in lines:
                            if line[-4:] == ' on\n':
                                s_state, s_game = get_AlarmState(line[:-4])
                                print('print line >'+line+'///'+s_state)
                                if s_state == 'on':
                                    user_on = user_on + str(line[:-4]) + '(ONLINE)' +' : '+s_game+'\n'
                                elif s_state == 'off':
                                    user_on = user_on + str(line[:-4]) + '(OFFLINE)' + '\n'

                            elif line[-4:] == 'off\n':
                                s_state, s_game = get_AlarmState(line[:-4])
                                print('print line >'+line+'///'+s_state)

                                if s_state == 'on':
                                    user_off = user_off + str(line[:-4]) + '(ONLINE)' +' : '+s_game+'\n'
                                elif s_state == 'off':
                                    user_off = user_off + str(line[:-4]) + '(OFFLINE)' + '\n'
                        
                        icon_url = 'https://cdn.discordapp.com/avatars/'+str(user_id) + '/' + u_state['avatar']+'.png'
                        embed = discord.Embed(title = f"", description = f"", color = 0x5882FA)
                        embed.set_author(name = u_state['username'], url = "", icon_url = icon_url)
                        embed.add_field(name = "> 스트리머 알림 ON", value = user_on, inline = False)
                        embed.add_field(name = "> 스트리머 알림 OFF", value = user_off, inline = False)
                        await m.send(embed=embed)

                    else :
                        for line in lines:
                            if line[-4:] == ' on\n':
                                user_on = user_on + str(line[:-4]) + '\n'
                            elif line[-4:] == 'off\n':
                                user_off = user_off + str(line[:-4]) + '\n'
                        
                        icon_url = 'https://cdn.discordapp.com/avatars/'+user_id + '/' + u_state['avatar']+'.png'
                        embed = discord.Embed(title = f"", description = f"", color = 0x5882FA)
                        embed.set_author(name = u_state['username'], url = "", icon_url = icon_url)
                        embed.add_field(name = "> 스트리머 알림 ON", value = user_on, inline = False)
                        embed.add_field(name = "> 스트리머 알림 OFF", value = user_off, inline = False)
                        await m.send(embed=embed)

                    f.close()

                # 파일 저장시 기본 off 설정
                # on은 없으면 추가 on로
                elif arg2 == 'add':
                    user_id = m.author.id
                    cnt = '0'

                    for line in lines:
                        if line[:-5] == arg1:
                            cnt = '1'

                    if cnt != '0':
                        embed = discord.Embed(title = f"", description = f"", color = 0xF16666)
                        embed.add_field(name = "> 이미 추가된 스트리머 입니다.", value = arg1, inline = False)
                        await m.send(embed=embed)
                    else: 
                        f = open(userfile+'.txt','a')
                        f.write(arg1+' off'+'\n')
                        f.close()
                        embed = discord.Embed(title = f"", description = f"", color = 0x5882FA)
                        embed.add_field(name = "> 스트리머가 추가되었습니다.", value = arg1, inline = False)
                        await m.send(embed=embed)

                elif arg2 == 'del':
                    user_id = m.author.id
                    cnt = '0'

                    #삭제할 행 줄번호
                    lineCnt = 0
                    lineNu = 0

                    for line in lines:
                        lineCnt += 1
                        if line[:-5] == arg1:
                            lineNu = lineCnt
                            cnt = '1'

                    if cnt != '0':
                        # 삭제될 행
                        #print('Be : '+str(lines[lineNu -1]))
                        lines[lineNu - 1] = '\n'
                        f = open(userfile+'.txt','w')
                        f.writelines(lines)
                        f.close()

                        embed = discord.Embed(title = f"", description = f"", color = 0x5882FA)
                        embed.add_field(name = "> 스트리머가 삭제되었습니다.", value = arg1, inline = False)
                        await m.send(embed=embed)
                    else: 
                        embed = discord.Embed(title = f"", description = f"", color = 0xF16666)
                        embed.add_field(name = "> 삭제할 스트리머가 없습니다.", value = arg1, inline = False)
                        await m.send(embed=embed)

                    print('in del')
                elif arg2 == 'off':
                    user_id = m.author.id
                    print('in off')
                elif arg2 == 'on':
                    user_id = m.author.id
                    print('in on')
                else:
                    print('in else')

                break
                
            else :
                f = open(userfile + ".txt", 'w')
                f.close()

        else :
            os.mkdir(srv_name)
'''    
    print(m.message.author)//사용자#숫자
    print(m.message.channel)//트위치
    print(m.message.guild)//서버 이름
    print(m.guild.icon_url)//서버 아이콘
'''

def get_AlarmState(s_id):
    print('get alarm state '+str(s_id))
    r, s_state, g_state = get_StreamToken(s_id)

    if s_state['data'][0]['is_live'] == True:
        print('streamer >on')
        s_state = 'on'
        s_game = g_state['data'][0]['game_name']
    else:
        print('streamer >off')
        s_state = 'off'
        s_game = ''

    return s_state, s_game




@client.command()
async def test(m, mem):
    print('print user >'+str(mem))

    print("user id > "+str(m.author.id))
    mem = mem[2:-1]
    url = f'https://discordapp.com/api/users/'+str(mem)
    header = {'Authorization': 'Bot '+ token}
    r = requests.get(url = url, headers = header)
    u_state = r.json()
    print(u_state['username'])
    
    print(u_state)
    url = f'https://discordapp.com/api/guilds/'+str(m.guild.id)+'/members'
    header = {'Authorization': 'Bot '+ token}
    r = requests.get(url = url, headers = header)
    g_state = r.json()
    
    print(g_state)

    print(type(mem))
    await m.send(str(u_state))

'''
@test.error
async def test_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        arg1 = '-d'
        await test(m, arg1)
'''

@client.command()
async def a(m, arg1, arg2):
    await alarm(m, arg1, arg2)


@client.command()
async def 레식(m):
    #user = client.get_user_info('')
    testm = '{0.author.mention}'.format(m)
    await m.send(testm)


#exeption
@streamer.error
async def streamer_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("잘못된 명령어 사용법입니다. \n/info를 참고해주세요.")
@s.error
async def s_error(ctx,error):
    await streamer_error(ctx,error)

@alarm.error
async def alarm_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        arg1 = 'state'
        arg2 = str(ctx.author.id)
        await alarm(ctx, arg1, arg2)

@a.error
async def a_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        arg1 = 'state'
        arg2 = str(ctx.author.id)
        await alarm(ctx, arg1, arg2)



client.run(token)
