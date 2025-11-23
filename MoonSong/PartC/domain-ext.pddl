(define (domain lunar-extended)
    (:requirements :strips :typing)

    (:types
        equipment
        rover - equipment
        lander - equipment
        location
        data
        scan - data
        image - data
        sample
        human
        astronaut
        internal_area
        control_room - internal_area
        docking_bay - internal_area
    )

    (:predicates
        (is_landed ?lan - lander) ;Whether a lander is landed or not.
        (is_deployed ?r - rover) ;Whether the rover is deployed or not.
        (is_area_of ?ia - internal_area ?lan - lander) ;Make sure the internal area is of the lander.
        (on_position ?e - equipment ?l - location) ;Whether an equipment is on a certain location or not.
        (is_connected ?l1 - location ?l2 - location) ;Whether two locations are connected or not.
        (need_image ?l - location ?i - image) ;This location needs take an image
        (need_sample ?l - location ?s - sample) ;This location needs take a sample
        (need_scan ?l - location ?sc - scan) ;This location needs take a scan
        (captured_data ?r - rover ?d - data) ;Rover r has captured data (image,scan).
        (collected_sample ?r - rover ?s - sample) ; Rover r has collected a sample.
        (empty_memory ?r - rover) ;Rover r has empty memory.
        (hand_empty ?r - rover);Rover r has empty hand.
        (is_full ?lan - lander) ;Lander is full with samples
        (has_received ?d - data);Data has been received.
        (sample_got ?s - sample);Sample has been received.
        (association ?lan - lander ?r - rover);Lander is associated with the rover.
        (astronaut_at ?a - astronaut ?l - lander ?ia - internal_area);astronaut at the internal area of lander
    )

    ;-------------------------------
    ; land
    ; -------------------------------
    ;Before the lander landing the lander and the rover are not anywhere
    ;This should be the first action for an undeployed rover
    ;And only perform once at beginning.
    (:action lander_land 
        :parameters (?lan - lander ?l - location)
        :precondition 
        (and
            (not (is_landed ?lan)) 
            )
        :effect 
        (and
            (is_landed ?lan)
            (on_position ?lan ?l)
        )
    )
    
    ;-------------------------------
    ; deploy rover
    ; ----------
    ; New added as we need to describe the deployment process of the rover.
    ; Because this action need the astronaut to be at the docking bay and the lander is landed.
    ; While the land action don't need the astronaut to be at the docking bay.  
    (:action rover_deploy
        :parameters (?r - rover ?lan - lander ?l - location ?a - astronaut ?doc - docking_bay)
        :precondition (and 
            (is_landed ?lan)
            (on_position ?lan ?l)
            (association ?lan ?r)
            (not (is_deployed ?r))
            (is_area_of ?doc ?lan)
            (astronaut_at ?a ?lan ?doc)

        )
        :effect (and 
            (is_deployed ?r)
            (on_position ?r ?l)
        )
    )
    
    ;-------------------------------
    ; rover move
    ; -------------------------------
    ;The graph is directed graph, so we choose to move from l1 to l2
    (:action rover_move
        :parameters (?l1 - location ?l2 - location ?r - rover)
        :precondition
        (and
            (not (on_position ?r ?l2))
            (on_position ?r ?l1)
            (is_connected ?l1 ?l2)
        )
        :effect
        (and
            (not (on_position ?r ?l1))
            (on_position ?r ?l2)
        )
    )
    
    ;-------------------------------
    ; take picture on location 
    ; -------------------------------
    ;This require the rover has an empty memory to store the image
    ;Also when a rover take the picture there is no need to take a picture again
    ;After that the rover is full so it can't store other data.
    (:action take_picture
        :parameters (?r - rover ?l - location ?i - image)
        :precondition
        (and
            (on_position ?r ?l)
            (need_image ?l ?i)
            (empty_memory ?r)
        )
        :effect
        (and
            (not (empty_memory ?r))
            (not (need_image ?l ?i))
            (captured_data ?r ?i)
        )
    )
    
    ;-------------------------------
    ; take scan on loctaiom
    ; -------------------------------
    ;The same action with take picture
    (:action take_scan
        :parameters (?r - rover ?l - location ?sc - scan)
        :precondition
        (and
            (on_position ?r ?l)
            (need_scan ?l ?sc)
            (empty_memory ?r)
        )
        :effect
        (and
            (not (empty_memory ?r))
            (not (need_scan ?l ?sc))
            (captured_data ?r ?sc)
        )   
    )
    
    ;-------------------------------
    ; take sample
    ; -------------------------------
    ;Sample need a position to grab, and it won't infuluence the storage of the data
    (:action take_sample
        :parameters (?r - rover ?l - location ?s - sample)
        :precondition
        (and
            (on_position ?r ?l)
            (need_sample ?l ?s)
            (hand_empty ?r)
            
            
        )
        :effect
        (and
            (not (need_sample ?l ?s))
            (not (hand_empty ?r))
            (collected_sample ?r ?s)
        )
    )
    
    ;-------------------------------
    ; transmit data back to lander
    ; -------------------------------
    ; Only when the astronaut is at the control room
    (:action transmit_data
        :parameters (?r - rover ?d - data ?lan - lander ?a - astronaut ?con - control_room)
        :precondition (and 
            (captured_data ?r ?d)
            (not (has_received ?d))
            (association ?lan ?r)
            (is_area_of ?con ?lan)
            (astronaut_at ?a ?lan ?con)
        ) 
        :effect (and
            (not (captured_data ?r ?d))
            (has_received ?d)
            (empty_memory ?r)
        )
    )
    

    ;-------------------------------
    ; take sample back to lander
    ; -------------------------------
    ; Rover need to put the sample into associated lander
    ; Only when the astronaut is at the docking bay
    (:action sample_receive
        :parameters (?lan - lander ?r - rover ?s - sample ?l - location ?a - astronaut ?doc - docking_bay)
        :precondition (and
            (not (is_full ?lan))
            (on_position ?r ?l)
            (on_position ?lan ?l)
            (association ?lan ?r)
            (collected_sample ?r ?s)
            (is_area_of ?doc ?lan)
            (astronaut_at ?a ?lan ?doc)
         )
        :effect (and 
            (is_full ?lan)
            (not (collected_sample ?r ?s))
            (hand_empty ?r)
            (sample_got ?s)
        )
    )

    ;-------------------------------
    ; Astronaut move inside a lander
    ; -------------------------------
    ; Astronaut can only move inside a lander
    (:action astronaut_move_internal
        :parameters (?a - astronaut ?lan - lander ?from - internal_area ?to - internal_area)
        :precondition 
        (and
            (astronaut_at ?a  ?lan  ?from )
            (is_area_of ?from ?lan )
            (is_area_of ?to ?lan )
            (not (= ?from ?to)) ; Cannot move to the same area
        )
        :effect 
        (and
            (not (astronaut_at ?a ?lan ?from))
            (astronaut_at ?a ?lan ?to)
        )
    )

)