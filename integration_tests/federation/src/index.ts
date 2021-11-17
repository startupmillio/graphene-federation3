import {ApolloServer} from 'apollo-server'
import {ApolloGateway} from '@apollo/gateway'

const serviceA_url: string = 'http://service_a:3000/graphql';
const serviceB_url: string = 'http://service_b:3000/graphql';
const serviceC_url: string = 'http://service_c:3000/graphql';
const serviceD_url: string = 'http://service_d:3000/graphql';

const gateway = new ApolloGateway({
    serviceList: [
        { name: 'service_a', url: serviceA_url },
        { name: 'service_b', url: serviceB_url },
        { name: 'service_c', url: serviceC_url },
        { name: 'service_d', url: serviceD_url },
    ],
});

const server = new ApolloServer({
    gateway,
    subscriptions: false
});

server.listen(3000).then(({ url }) => {
  console.log(`🚀 Server ready at ${url}`);
});
