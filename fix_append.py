#!/usr/bin/env python3
import json

appends = {
    2: (
        " It would astonish you how social intercourse and a simple exam of the books, especially under the law, can restore balance. The adviser, awfully tired, chose to delegate tasks rather than damn the staff or let stress afflict and cripple morale. He cut his caffeine intake, booked a massage, and avoided the rigid hierarchy. Inevitably, with countable wins and a plastic spray of optimism, the town recovered.",
        "你会惊讶于社会交往和对账目的一次检查，尤其是在法律之下，竟能恢复平衡。那位顾问累得要命，选择把任务委派出去，而不是责骂员工或让压力折磨并削弱士气。他减少了咖啡因的摄入，预约了按摩，避开僵化的等级制度。最终，凭着可数的胜利和一抹塑料般的乐观，小镇得以复苏。",
    ),
    3: (
        " Suppose, after a big game of badminton, the team gathered for a briefing that felt almost like a ritual or a sermon. One advocate would dislike the seductive but ostensible promises of easy profit; such talk could exasperate anyone. They discussed a paternity case, a pregnant pause in trade as the firm planned to reexport goods, and even the parking crisis, before each encounter ended in agreement.",
        "假设在一场盛大的羽毛球比赛之后，球队聚在一起开了个简报会，那气氛几乎像一场仪式或布道。一位倡导者会厌恶那些诱人却表面的轻松获利承诺；这种话能激怒任何人。他们讨论了一桩亲子关系案件、贸易中怀孕般的停顿（公司计划把货物再出口），甚至还有停车难题，最后每一次交锋都以一致同意收场。",
    ),
    4: (
        " Along the road, the journey hit a snag. Our guide, once a pupil of an old conqueror's tale, tried to reassure us and converse calmly, though his nasal voice carried an uncomfortable edge. He would not edit the truth or add fluff: the arbitrary bill for the ferry was a pitfall, a real detriment to efficiency. To persuade the crowd, he raised an outcry against waste, explaining how industrialized agriculture could distend budgets. The implication was clear, sharp as a stab; even a disabled cart on our flank felt the hardness of the climb. They agreed to release the funds, and added a small suffix of thanks to the contract.",
        "沿着这条路，旅程遇到了障碍。我们的向导曾是一位老征服者故事的学生，他努力让我们安心，平静地交谈，尽管他带鼻音的嗓音透着一丝令人不适的意味。他不愿粉饰真相或添加废话：渡船那笔武断的账单是个陷阱，是对效率的真正损害。为了说服众人，他大声疾呼反对浪费，解释工业化农业如何让预算膨胀。其含义如刀刺般清晰；连我们侧翼一辆抛锚的残破推车也感受到攀爬的艰难。他们同意拨款，并在合同上加了一小段感谢的后缀。",
    ),
    5: (
        " I have to ask: what is the scope of a single show? The performance itself could stagger you. One act mixed gymnastics and boxing; a dancer in a bright skirt would tilt and balance on one leg, graceful as a lioness. A puppet shaped like a sphinx rose on a periscope-like pole with a click, while a paper cock crowed. Behind the scenes, the air-conditioning hummed, and a coalition of stagehands tried to delete every flaw and avoid ineffectiveness. There was no illegal trick, no effluent dumped from the kitchen where they served pie. Yet turmoil nearly arrived: a sponsor's resignation, a late notification, a predisposition to panic. They had to commit, to shear away the fluff, to fork over more cash, to cruise past the danger and not dump the project. The crew could arrest the chaos, restore digestion of the schedule, and the reproduction of the act ran like clockwork. After a quick shampoo of fresh ideas, they angled it from a new angle and turned a likely defeat into triumph.",
        "我不得不问：一场演出的范围有多大？演出本身就能让你目瞪口呆。有一幕融合了体操与拳击；一位身着鲜艳裙子的舞者单腿倾斜并保持平衡，优雅如母狮。一个斯芬克斯造型的木偶随着一声咔哒声沿潜望镜般的杆子升起，一只纸公鸡随之啼鸣。后台空调嗡嗡作响，一群舞台工作人员组成的联盟努力删除每一处瑕疵，避免低效。没有任何非法把戏，厨房（供应派饼之处）也没有排放污水。然而骚乱险些降临：一位赞助商辞职、一份迟到的通知、一种易于恐慌的倾向。他们必须全力以赴，剪掉冗余，掏出更多现金，平稳驶过险境而不放弃项目。剧组制止了混乱，恢复了日程的消化，节目的再现如钟表般精准。在新点子洗礼之后，他们换了个角度，把可能的失败变成了胜利。",
    ),
    6: (
        " Consider a business as varied as a ship's berth. Good utilization of every asset matters, from the radial tires on the jet-black delivery van to the visual displays in the showroom. A bony old manager in a mackintosh, who loved gardening on weekends, wrote plain prose, not raucous colloquial slogans. He kept aspirin in his pocket for headaches, a tube of cream for his hands, and a mythical calm that could frighten rivals. He noted the asymmetry in the market like a tiger watching prey, sought the shade of caution, and treated each setback as an exoneration rather than defeat, as if a healthy gland of optimism fed a whole regiment of staff.",
        "想想一桩像船舶泊位一样多样的生意。每一项资产的利用都很重要，从送货厢式车上的子午线轮胎到陈列室里的视觉展示。一位身材瘦削、穿着雨衣、周末爱好园艺的老经理，写朴实的散文，而非沙哑的口语口号。他口袋里备着阿司匹林治头痛，一支护手霜，以及一种能吓退对手的神话般的镇定。他像老虎盯猎物般注意市场的不对称，寻求谨慎的荫蔽，把每次挫折当作昭雪而非失败，仿佛一枚乐观的腺体滋养着整团员工。",
    ),
    7: (
        " Over a long lunch, the deputy and an emigrant banker discussed capitalism as a pillar of society. It would perplex anyone how a unilateral statute on lending could sweeten or sour a partnership. They refused to adopt a dummy policy or misappropriate funds; that would be pathological, leaving only a semblance of order. Off the congested street, near a yacht club, they read an anthology of essays on unemloyment, housework, and the urge to incline toward reform. A cuckoo called; a footstep echoed. One pulled a stocking of coins from a vacuum-sealed box, noting how iron oxide had stained it, and added reinforcement to their plan.",
        "在一顿漫长的午餐中，那位副手和一位移居海外的银行家谈论资本主义这一社会支柱。一项关于借贷的单边法令竟能让合伙关系变甜或变坏，这会让任何人困惑。他们拒绝采用傀儡政策或盗用资金；那将是病态的，只留下秩序的表象。在拥挤街道之外、游艇俱乐部附近，他们读了一本关于失业、家务以及倾向改革的文集。一只布谷鸟鸣叫，一阵脚步声回响。一人从真空密封盒里取出一只装着硬币的长袜，注意到氧化铁已把它染色，并为他们的计划增添了强化的力量。",
    ),
    8: (
        " Ask yourself why some mysteries never wither. A teacher, my spouse's old mentor, would attend every lecture, preferring a sonnet to empty rhetoric. The bugbear of the age was disease: poliomyelitis and malnutrition, which could paralyse a child as surely as sorrow. It was inevitable, he said, that someone else would solve it. He kept a pad of notes, a needle and thread, and a tin of pilchard for the road. On the twelfth of the ultimo month, riding neither pony nor motorcycle but in transit by train, he reached the junction near the moor. He would lend a hand to anyone, gross profit or not, studying Leninism with the innocence of a student, dipping a solvent to clean an old b/l document. The market was bearish, but his faith was solvent. Years earlier he had judged a contestant in a poetry duel, awarding the prize to the one whose verse showed true innocence.",
        "问问你自己，为何有些谜团永不凋零。一位老师，我配偶的旧日导师，会出席每一场讲座，宁愿读十四行诗也不愿听空洞的花言巧语。那个时代的梦魇是疾病：小儿麻痹症和营养不良，它们能像悲伤一样使一个孩子瘫痪。他说，迟早会有别人解决它，这是不可避免的。他随身带着一叠笔记、一根针线，以及一罐路上吃的沙丁鱼。在上个月的十二号，他既不骑小马也不骑摩托车，而是乘火车中转，抵达沼泽附近的交叉路口。无论毛利与否，他都愿向任何人伸出援手，怀着学生般的纯真研究列宁主义，蘸着溶剂清理一份旧提单。市场看跌，但他的信念依然稳健。多年前他曾在一场诗歌对决中担任评委，把奖项授予诗句中流露真正纯真的那位参赛者。",
    ),
    9: (
        " To avert disaster, the citizens signed a petition. A famous quotation, often misquoted, became their lever: every participant could specialize in one task. The chatter in the limousine turned serious; a careless interpretation, a backward step, could rupture the fragile peace and tangle the talks. A billion small choices, like a stroke of a pen, could kill or save the plan. They would not charge like a bull; instead they shared a warm hug, used every device of diplomacy, and refused to let the moment slip.",
        "为避免灾难，市民们签署了一份请愿书。一句常被误引的名言成了他们的杠杆：每位参与者都能专攻一项任务。豪华轿车里的闲谈变得严肃；一个草率的解释、一步倒退，都可能使脆弱的和平破裂并使谈判陷入纠缠。十亿个小小的选择，如同一笔落下，能毁掉或拯救计划。他们不会像公牛般横冲直撞；相反，他们温暖地拥抱，动用一切外交手段，拒绝让时机溜走。",
    ),
    10: (
        " It is ironical, almost a trifle, how a short inquiry can change everything. An entrepreneur, no flabby dreamer, refused to be the scapegoat for a failed nomination. He would uncap a bottle, enclose a note, and never interrupt a guest. The lab measured temperature in Fahrenheit, tested a hydrogen sulphide sample at full saturation, and studied the componential and constitutive parts of a new alloy, recording each subsequence with care. A sullen technician, doing a sampling of the metal's innards, traced a thin artery of rust along the beam. Even the lord of the estate, who kept a tame panda in mind as a symbol of calm, called it constitutive of progress, not a trifle.",
        "颇具讽刺意味的是，几乎是件小事——一次简短的询问就能改变一切。一位企业家，绝非优柔寡断的空想者，拒绝为一次失败的提名当替罪羊。他会拧开瓶盖，附上一张便条，从不打断客人。实验室用华氏温度计测温，在完全饱和状态下测试硫化氢样品，研究新合金的成分构成与构成性部分，仔细记录每一个后续结果。一位绷着脸的技师对金属内脏做抽样，沿着横梁追踪一条细细的锈蚀动脉。连庄园的主人——他心中养着一只象征平静的温顺熊猫——也称这是进步的构成要素，而非区区小事。",
    ),
}

for pid, (en, zh) in appends.items():
    path = f"out/out_{pid:03d}.json"
    obj = json.load(open(path, encoding="utf-8"))
    obj["text"] = obj["text"].rstrip() + en
    obj["translation"] = obj["translation"].rstrip() + zh
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False)
print("done")
