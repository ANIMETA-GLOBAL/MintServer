import { Metaplex, keypairIdentity, bundlrStorage } from "@metaplex-foundation/js";
import { Connection, clusterApiUrl, Keypair, PublicKey } from "@solana/web3.js";
import { createClient } from 'redis';
const redispwd = process.env.REDISPWD
const client = createClient({
    socket: {
        host: "211.149.170.109",
    },
    password: redispwd

});
const connection = new Connection(clusterApiUrl("devnet"));

client.on('error', (err) => console.log('Redis Client Error', err));

await client.connect();

const wallet = Keypair.generate();

const metaplex = Metaplex.make(connection)
    .use(keypairIdentity(wallet))
    .use(bundlrStorage());


async function findNft(ownerAddress) {
    console.log()
    const account = new PublicKey(ownerAddress);
    const nft = await metaplex.nfts().findAllByOwner(account).run();
    return nft
}


const subscriber = client.duplicate();
await subscriber.connect();

await subscriber.subscribe('rq_solana', (message) => {
    // console.log(message); // 'message'
    var request = JSON.parse(message);

    try {

        if (request.function == "getAllByOwner" && request.args.address) {
            console.log("receipt getAllByOwner:");
            console.log(request.args.address);
            client.set(request.id,message);
            findNft(request.args.address).then(res => {
                console.log(res)
                client.set(request.id, JSON.stringify(res))
            })
        }
    } catch (error) {
        client.set(request.id,error)
    }

});

