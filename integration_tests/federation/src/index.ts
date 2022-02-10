import {ApolloServer} from 'apollo-server'
import {
    ApolloGateway,
    IntrospectAndCompose,
} from '@apollo/gateway'

const gateway = new ApolloGateway({
    supergraphSdl: new IntrospectAndCompose({
        subgraphs: [
            {name: 'service_a', url: 'http://service_a:3000/graphql'},
            {name: 'service_b', url: 'http://service_b:3000/graphql'},
            {name: 'service_c', url: 'http://service_c:3000/graphql'},
            {name: 'service_d', url: 'http://service_d:3000/graphql'},
        ]
    }),
});

const server = new ApolloServer({
    gateway,
});

server.listen(3000).then(({url}) => {
    console.log(`🚀 Server ready at ${url}`);
});
