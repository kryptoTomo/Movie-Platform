import { Fragment, useState, useEffect } from "react";
import { Card, Form, Col, Button, Row, Stack, Table, Alert } from 'react-bootstrap';
import axios from "./../axios";


const Recommender = (props) => {

    useEffect(()=>{
        handleGetFriends();
        handleGetRecommendations();
    }, [])

    const [foundAny, setFoundAny] = useState(false);
    const [foundAnyNew, setFoundAnyNew] = useState(false);

    const handleSubmitForm = (event) => {
        event.preventDefault()
        var loc = event.target[0].value;
        var qui = event.target[1].value;
        var friendList = "";
        var iter = 2
        friends.forEach( fri => {
            if(event.target[iter].checked){
                friendList += fri + ",";
            }
            iter += 1;
        })
        friendList = friendList.slice(0, -1);

        axios.post("/get-best", {cuisine: qui, location: loc, person: friendList, max: "True"})
        .then(res => {
            if(res.data.length === 0){
                setFoundAny(true)
            }
        }).catch(err => {
            console.log(err.message)
        })

    }

    const [friends, setFriends] = useState([])
    const [newRest, setNewRest] = useState([])

    const handleGetFriends = () => {
        axios.get(`/get-friends?person=${props.userName}`)
        .then(res => {
            console.log(res)
            setFriends(res.data.friends)
        }).catch(err => {
            console.log(err.message)
        })
    }

    // this not working wanna know why
    const handleGetRecommendations = () => {
        axios.get(`/get-recommendations?person=${props.userName}`)
        .then(res => {
            if(res.data.recommendations.length === 0){
                setFoundAnyNew(true)
            }
            setNewRest(res.data.recommendations)
        }).catch(err => {
            console.log(err.message)
        })
    }


    let newRestRows = newRest.map((res, index) => {
        return (
            <tr>
                <td>{index+1}</td>
                <td>{res.name}</td>
                <td>{res.recommenders.map(el => el + " ")}</td>
                <td>{res.count}</td>
            </tr>)
    })

    const infoFoundAnyNew = (
        <Alert variant="dark" onClose={() => setFoundAnyNew(false)} dismissible>
            <Alert.Heading>No c????...</Alert.Heading>
            <p>
            Na to wygl??da ??e znasz ju?? wszystkie miejsca preferowane przez twoich znajomych, wi??c nic nowego nie mo??emy ci poleci??!
            </p>
      </Alert>
    )

    return(
        <Fragment>

        <Card style={{margin: "30px"}}>
            <Card.Body>
                {foundAnyNew ? infoFoundAnyNew : null}
                <Card.Title>Poznaj Filmy Twoich Znajomych!</Card.Title>
                <Card.Text>
                W tej rubryce znajdziesz list?? film??w, kt??re s?? lubiane przez twoich znajomych, ale ty jeszcze ich nie odwiedza??e?? (nie s?? na li??cie polubionych przez ciebie).
                </Card.Text>
                <Table striped bordered hover className="FilmTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Tytu??</th>
                            <th>Polecaj??cy</th>
                            <th>Ilo???? polece??</th>
                        </tr>
                    </thead>
                    <tbody>
                        {newRestRows}
                    </tbody>
                </Table>
            </Card.Body>
        </Card>

      </Fragment>
    );
}

export default Recommender;